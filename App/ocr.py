import os
import cv2
import numpy as np
import pytesseract
import pdf2image
import docx2txt
import tempfile
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import torch
from pathlib import Path

# Set Tesseract path if not in PATH - uncomment and set your path if needed
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # or your actual tesseract path

# Download YOLOv5 for handwriting detection
def get_yolo_model():
    """Load YOLOv5 model for handwriting detection"""
    # Check if model exists, download only once
    if not os.path.exists('yolov5s.pt'):
        # Use torch hub to download YOLOv5
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    else:
        model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')
    return model

def is_handwritten(image_np):
    """Detect if image contains handwriting using image characteristics"""
    # Convert to grayscale if it's not
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_np
        
    # Apply Canny edge detection to find edges
    edges = cv2.Canny(gray, 50, 150)
    
    # Count non-zero pixels (edges)
    edge_count = np.count_nonzero(edges)
    
    # Get image dimensions
    height, width = gray.shape
    total_pixels = height * width
    
    # Calculate edge density
    edge_density = edge_count / total_pixels
    
    # Estimate stroke width variation using morphological operations
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(gray, kernel, iterations=1)
    eroded = cv2.erode(gray, kernel, iterations=1)
    stroke = cv2.subtract(dilated, eroded)
    
    # Calculate stroke width variation
    stroke_std = np.std(stroke[stroke > 0]) if np.count_nonzero(stroke) > 0 else 0
    
    # Handwritten text typically has higher edge density and stroke width variation
    return edge_density > 0.05 and stroke_std > 15

def preprocess_image(image_np):
    """Enhance image for better OCR results"""
    # Convert to grayscale
    if len(image_np.shape) == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    else:
        gray = image_np
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Noise removal using morphological operations
    kernel = np.ones((1, 1), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Dilation to make characters clearer
    kernel = np.ones((1, 1), np.uint8)
    dilated = cv2.dilate(opening, kernel, iterations=1)
    
    return dilated

def recognize_handwriting(input_file):
    """Process handwriting in uploaded file and extract text"""
    # Create temp file to handle uploaded file properly
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(input_file.name).suffix) as tmp:
        tmp.write(input_file.getvalue())
        temp_path = tmp.name
    
    try:
        # Determine file type by extension
        file_ext = Path(input_file.name).suffix.lower()
        
        if file_ext in ['.pdf']:
            extracted_text = extract_text_from_pdf(temp_path)
        elif file_ext in ['.docx', '.doc']:
            extracted_text = extract_text_from_docx(temp_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            extracted_text = extract_text_from_image(temp_path)
        else:
            extracted_text = "Unsupported file format. Please upload PDF, DOCX, or common image formats."
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return extracted_text

def extract_text_from_pdf(file_path):
    """Extract text from PDF files, handling both digital and scanned content"""
    full_text = ""
    
    try:
        # First try PyMuPDF for digital PDF text extraction
        doc = fitz.open(file_path)
        digital_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            digital_text += page.get_text()
        
        # If digital text extraction yields significant content, use it
        if len(digital_text.strip()) > 100:  # Arbitrary threshold
            return digital_text
        
        # Otherwise, treat as scanned PDF and use OCR
        images = pdf2image.convert_from_path(file_path)
        
        for i, image in enumerate(images):
            # Convert PIL Image to numpy array for OpenCV
            image_np = np.array(image)
            
            # Check if page contains handwriting
            if is_handwritten(image_np):
                # Use handwritten-specific OCR settings
                preprocessed = preprocess_image(image_np)
                page_text = pytesseract.image_to_string(
                    Image.fromarray(preprocessed),
                    config='--psm 6 --oem 1 -l eng'
                )
            else:
                # Use standard OCR settings for printed text
                page_text = pytesseract.image_to_string(
                    image,
                    config='--psm 3 --oem 1 -l eng'
                )
            
            full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        return full_text.strip()
    
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def extract_text_from_docx(file_path):
    """Extract text from DOCX files"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        return f"Error processing DOCX: {str(e)}"

def extract_text_from_image(file_path):
    """Extract text from image files with handwriting detection"""
    try:
        # Read the image
        image_np = cv2.imread(file_path)
        
        # Check if image contains handwriting
        handwritten = is_handwritten(image_np)
        
        if handwritten:
            # Apply special preprocessing for handwritten text
            preprocessed = preprocess_image(image_np)
            
            # Use specialized OCR settings for handwriting
            text = pytesseract.image_to_string(
                Image.fromarray(preprocessed),
                config='--psm 6 --oem 1 -l eng'
            )
            
            # If text is still sparse, try YOLO for handwriting detection
            if len(text.strip().split()) < 10:
                # Use YOLO to detect handwritten regions
                model = get_yolo_model()
                results = model(image_np)
                
                # Extract detected regions and perform OCR on each
                detected_text = ""
                for i, (xmin, ymin, xmax, ymax, conf, cls) in enumerate(results.xyxy[0]):
                    if conf > 0.35:  # Confidence threshold
                        # Extract the region
                        roi = image_np[int(ymin):int(ymax), int(xmin):int(xmax)]
                        if roi.size > 0:
                            # Preprocess and OCR the region
                            roi_processed = preprocess_image(roi)
                            region_text = pytesseract.image_to_string(
                                Image.fromarray(roi_processed),
                                config='--psm 6 --oem 1 -l eng'
                            )
                            detected_text += region_text + "\n"
                
                # Use detected text if better than initial OCR
                if len(detected_text.strip()) > len(text.strip()):
                    text = detected_text
                
            return "Handwritten Text Detected:\n" + text
        else:
            # Standard OCR for printed text
            text = pytesseract.image_to_string(
                image_np,
                config='--psm 3 --oem 1 -l eng'
            )
            return text
    
    except Exception as e:
        return f"Error processing image: {str(e)}"

def extract_medical_entities(text):
    """Extract medical entities from the OCR text (medications, dosages, lab values)"""
    # Basic medical entity extraction - in a real app, you'd use a more sophisticated NER model
    
    # Common medication names and their variations
    common_meds = [
        'acetaminophen', 'tylenol', 'paracetamol', 'ibuprofen', 'advil', 'motrin',
        'aspirin', 'lisinopril', 'metformin', 'lipitor', 'atorvastatin', 'amoxicillin',
        'metoprolol', 'amlodipine', 'albuterol', 'omeprazole', 'losartan', 'gabapentin',
        'hydrochlorothiazide', 'hctz', 'simvastatin', 'levothyroxine', 'azithromycin'
    ]
    
    # Lab test markers
    lab_tests = [
        'wbc', 'rbc', 'hgb', 'hct', 'platelets', 'glucose', 'bun', 'creatinine', 'sodium',
        'potassium', 'chloride', 'calcium', 'cholesterol', 'triglycerides', 'hdl', 'ldl',
        'a1c', 'tsh', 't3', 't4', 'alt', 'ast', 'alp', 'ggt', 'total bilirubin'
    ]
    
    # Extract medications
    medications = []
    for med in common_meds:
        if med.lower() in text.lower():
            # Try to find dosage near medication name
            med_index = text.lower().find(med.lower())
            context = text[max(0, med_index-20):min(len(text), med_index+50)]
            medications.append(context)
    
    # Extract lab values
    lab_values = []
    for lab in lab_tests:
        if lab.lower() in text.lower():
            # Try to find value near lab test name
            lab_index = text.lower().find(lab.lower())
            context = text[max(0, lab_index-10):min(len(text), lab_index+30)]
            lab_values.append(context)
    
    return {
        "medications": medications,
        "lab_values": lab_values,
        "full_text": text
    }

# Main function to handle all document types
def process_medical_document(input_file):
    """Process any medical document and extract relevant information"""
    text = recognize_handwriting(input_file)
    return extract_medical_entities(text)

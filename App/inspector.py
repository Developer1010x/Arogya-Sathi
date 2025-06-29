"""
Optimized File Integrity Inspector for Arogya-Sathi Application
"""
import os
import sys
import json
import hashlib
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import logging
import tempfile
from typing import Dict, List, Tuple, Optional

# Repository configuration
REPO_URL = "https://github.com/Developer1010x/Arogya-Sathi.git"
REPO_BRANCH = "main"

# Required files structure (grouped by type for better organization)
REQUIRED_FILES = {
    "python_files": [
        "app.py", "app1.py", "app2.py", "app3.py", "app4.py", "app5.py",
        "app6.py", "app7.py", "app9.py", "appo.py",
        "llm.py", "Config.py", "ocr.py", "sidebar.py", "utils.py", "vgg.py",
        "Operation.py", "Patient.py", "Person.py", "Doctor.py", "Nurse.py", "Hospital.py",
        "rcnnres.py",
    ],
    "weight_files": [
        "model_vgg.pt", "Resnet.pt", "yoloV8_medium.pt", "yolov8.pt"
    ],
    "model_files": [
        "yolo11n.pt", "yolov5s.pt"
    ],
    "image_files": [
        "images/medical.jpg"
    ],
    "directories": [
        "images", "weights", "notebooks", "test_images", "__pycache__"
    ]
}

OPTIONAL_FILES = [
    "requirements.txt", "README.md", ".gitignore", "LICENSE"
]

class FileInspector:
    def __init__(self, app_dir: Optional[str] = None):
        self.app_dir = Path(app_dir) if app_dir else Path.cwd()
        self.logs_dir = self.app_dir / "app_inspector"
        self._ensure_logs_directory()
        self.log_file = self.logs_dir / "inspection_log.txt"
        self.backup_dir = self.logs_dir / "backup"
        self.temp_repo_dir = None
        self.logger = self._setup_logging()
        
    def _ensure_logs_directory(self):
        """Ensure the logs directory exists"""
        self.logs_dir.mkdir(exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup optimized logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)
        
        # Stream handler (console)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
        return logger
        
    def quick_scan(self) -> Dict:
        """Optimized quick scan that only checks file existence"""
        results = {
            "missing_files": [],
            "present_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Use pathlib's glob for faster directory scanning
        existing_files = {str(p.relative_to(self.app_dir)) for p in self.app_dir.rglob('*')}
        
        for category, files in REQUIRED_FILES.items():
            for file_path in files:
                if file_path in existing_files:
                    results["present_files"].append(file_path)
                else:
                    results["missing_files"].append(file_path)
        
        return results
    
    def inspect_files(self) -> Dict:
        """Comprehensive file inspection with metadata"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "missing_files": [],
            "present_files": [],
            "corrupted_files": [],
            "file_details": {}
        }
        
        for category, files in REQUIRED_FILES.items():
            for file_path in files:
                file_info = self._get_file_info(file_path)
                file_info["category"] = category
                
                results["file_details"][file_path] = file_info
                
                if file_info["exists"]:
                    results["present_files"].append(file_path)
                else:
                    results["missing_files"].append(file_path)
        
        return results
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Helper method to get file info with caching"""
        full_path = self.app_dir / file_path
        if not full_path.exists():
            return {"exists": False}
        
        try:
            stat = full_path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_dir": full_path.is_dir(),
                "hash": self._get_file_hash(full_path) if not full_path.is_dir() else None
            }
        except Exception as e:
            self.logger.warning(f"Error checking {file_path}: {str(e)}")
            return {"exists": False}
    
    def _get_file_hash(self, file_path: Path) -> Optional[str]:
        """Optimized file hashing with buffer"""
        try:
            hash_md5 = hashlib.md5()
            with file_path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def restore_files(self, missing_files: List[str]) -> Tuple[List[str], List[str]]:
        """Optimized file restoration with parallel downloads"""
        if not missing_files:
            return [], []
            
        if not self._clone_repository():
            return [], missing_files
            
        restored = []
        failed = []
        
        try:
            repo_path = Path(self.temp_repo_dir)
            for file_path in missing_files:
                if self._restore_single_file(repo_path / file_path, self.app_dir / file_path):
                    restored.append(file_path)
                else:
                    failed.append(file_path)
        finally:
            self._cleanup_temp_dir()
            
        return restored, failed
    
    def _restore_single_file(self, src: Path, dst: Path) -> bool:
        """Helper to restore a single file/directory"""
        try:
            if not src.exists():
                return False
                
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            return True
        except Exception as e:
            self.logger.error(f"Restore failed for {dst}: {str(e)}")
            return False
    
    def _clone_repository(self) -> bool:
        """Optimized repository cloning with timeout"""
        try:
            self.temp_repo_dir = tempfile.mkdtemp(prefix="arogya_sathi_")
            cmd = ["git", "clone", "--depth", "1", "-b", REPO_BRANCH, REPO_URL, self.temp_repo_dir]
            subprocess.run(cmd, check=True, timeout=300)
            return True
        except Exception as e:
            self.logger.error(f"Clone failed: {str(e)}")
            return False
    
    def _cleanup_temp_dir(self):
        """Safe cleanup of temporary directory"""
        if self.temp_repo_dir and os.path.exists(self.temp_repo_dir):
            try:
                shutil.rmtree(self.temp_repo_dir)
            except Exception as e:
                self.logger.warning(f"Cleanup failed: {str(e)}")

    def save_inspection_report(self, results: Dict) -> Path:
        """Save inspection report to the app_inspector folder"""
        report_file = self.logs_dir / f"inspection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with report_file.open('w') as f:
            json.dump(results, f, indent=2)
        return report_file

if __name__ == "__main__":
    from argparse import ArgumentParser
    
    parser = ArgumentParser(description="File Integrity Inspector")
    args = parser.parse_args()
    
    inspector = FileInspector()
    results = inspector.quick_scan()
    inspector.save_inspection_report(results)

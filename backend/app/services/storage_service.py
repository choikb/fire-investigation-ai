"""
파일 스토리지 서비스 (MinIO/S3)
"""
import os
import hashlib
import shutil
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """증거 자료 저장 서비스"""
    
    def __init__(self):
        self.base_path = Path("storage/evidence")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # MinIO 클라이언트 초기화 (실제 배포 시)
        self.minio_client = None
        if settings.MINIO_ENDPOINT:
            try:
                from minio import Minio
                self.minio_client = Minio(
                    settings.MINIO_ENDPOINT,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=settings.MINIO_SECURE
                )
                # 버킷 생성
                if not self.minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
                    self.minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            except Exception as e:
                print(f"MinIO 연결 실패 (로컬 모드 사용): {e}")
    
    async def save_file(
        self, 
        file: UploadFile, 
        investigation_id: int,
        file_name: str
    ) -> Tuple[str, str]:
        """
        파일 저장 및 해시 계산
        
        Returns:
            (file_path, sha256_hash)
        """
        # 파일 확장자 확인
        ext = Path(file_name).suffix.lower()
        
        # 저장 경로 생성
        investigation_dir = self.base_path / str(investigation_id)
        investigation_dir.mkdir(exist_ok=True)
        
        # 고유 파일명 생성 (타임스탬프 + 원본명)
        import time
        timestamp = int(time.time())
        safe_name = f"{timestamp}_{file_name}"
        file_path = investigation_dir / safe_name
        
        # 파일 저장 및 해시 계산
        sha256_hash = hashlib.sha256()
        
        contents = await file.read()
        sha256_hash.update(contents)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # MinIO 업로드 (설정된 경우)
        if self.minio_client:
            try:
                object_name = f"{investigation_id}/{safe_name}"
                self.minio_client.put_object(
                    settings.MINIO_BUCKET_NAME,
                    object_name,
                    io.BytesIO(contents),
                    len(contents),
                    content_type=file.content_type
                )
                return f"s3://{settings.MINIO_BUCKET_NAME}/{object_name}", sha256_hash.hexdigest()
            except Exception as e:
                print(f"MinIO 업로드 실패, 로컬 저장: {e}")
        
        return str(file_path), sha256_hash.hexdigest()
    
    def get_file(self, file_path: str) -> Optional[bytes]:
        """파일 읽기"""
        if file_path.startswith("s3://"):
            # MinIO에서 읽기
            if self.minio_client:
                try:
                    parts = file_path.replace("s3://", "").split("/", 1)
                    bucket, object_name = parts[0], parts[1]
                    response = self.minio_client.get_object(bucket, object_name)
                    return response.read()
                except Exception as e:
                    print(f"MinIO 읽기 실패: {e}")
            return None
        else:
            # 로컬 파일 읽기
            path = Path(file_path)
            if path.exists():
                return path.read_bytes()
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            if file_path.startswith("s3://"):
                if self.minio_client:
                    parts = file_path.replace("s3://", "").split("/", 1)
                    bucket, object_name = parts[0], parts[1]
                    self.minio_client.remove_object(bucket, object_name)
            else:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
            return True
        except Exception as e:
            print(f"파일 삭제 오류: {e}")
            return False


# 전역 인스턴스
import io
storage_service = StorageService()

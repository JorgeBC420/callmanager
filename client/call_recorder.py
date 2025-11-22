"""
Sistema de Grabación de Llamadas - CallManager
Grabación de audio completo de llamadas con metadatos

Autor: CallManager System
Versión: 1.0
"""

import os
import logging
import threading
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import wave
import pyaudio

logger = logging.getLogger(__name__)


class CallRecorder:
    """Grabador de llamadas de audio"""
    
    def __init__(self, recordings_dir: str = "recordings", sample_rate: int = 44100):
        """
        Inicializar grabador
        
        Args:
            recordings_dir: Directorio para almacenar grabaciones
            sample_rate: Frecuencia de muestreo (Hz)
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)
        
        self.sample_rate = sample_rate
        self.chunk_size = 1024
        self.channels = 1  # Mono
        self.audio_format = pyaudio.paFloat32
        
        self.is_recording = False
        self.current_file: Optional[str] = None
        self.current_metadata: Optional[Dict] = None
        self.audio_thread: Optional[threading.Thread] = None
        
        # Audio device
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        
        logger.info("🎙️ CallRecorder inicializado")
    
    def start_recording(
        self,
        contact_name: str,
        contact_phone: str,
        user_id: str,
        user_name: str,
        call_id: str
    ) -> str:
        """
        Iniciar grabación de llamada
        
        Returns:
            Recording ID
        """
        if self.is_recording:
            logger.warning("⚠️ Ya hay una grabación activa")
            return ""
        
        try:
            # Crear nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            recording_id = f"{call_id}_{timestamp}"
            file_path = self.recordings_dir / f"{recording_id}.wav"
            
            # Guardar metadata
            self.current_metadata = {
                "recording_id": recording_id,
                "call_id": call_id,
                "contact_name": contact_name,
                "contact_phone": contact_phone,
                "user_id": user_id,
                "user_name": user_name,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "duration_seconds": 0,
                "file_path": str(file_path),
                "file_size_bytes": 0,
                "status": "recording"
            }
            
            # Abrir stream de audio
            self.stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            self.current_file = str(file_path)
            
            # Iniciar thread de grabación
            self.audio_thread = threading.Thread(
                target=self._recording_thread,
                daemon=True
            )
            self.audio_thread.start()
            
            logger.info(f"🔴 Grabación iniciada: {recording_id}")
            return recording_id
        
        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            self.is_recording = False
            return ""
    
    def stop_recording(self) -> Dict:
        """
        Detener grabación
        
        Returns:
            Metadata de la grabación
        """
        if not self.is_recording:
            logger.warning("⚠️ No hay grabación activa")
            return {}
        
        try:
            self.is_recording = False
            
            # Cerrar stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Esperar a que termine el thread
            if self.audio_thread:
                self.audio_thread.join(timeout=5)
            
            # Actualizar metadata
            if self.current_metadata:
                end_time = datetime.now()
                self.current_metadata['end_time'] = end_time.isoformat()
                self.current_metadata['status'] = 'completed'
                
                # Calcular duración
                if self.current_file and os.path.exists(self.current_file):
                    file_size = os.path.getsize(self.current_file)
                    self.current_metadata['file_size_bytes'] = file_size
                    
                    # Calcular duración desde el archivo WAV
                    try:
                        with wave.open(self.current_file, 'rb') as wav_file:
                            frames = wav_file.getnframes()
                            rate = wav_file.getframerate()
                            duration = frames / rate
                            self.current_metadata['duration_seconds'] = int(duration)
                    except:
                        pass
                
                # Guardar metadata en JSON
                metadata_file = self.current_file.replace('.wav', '_metadata.json')
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_metadata, f, indent=2, ensure_ascii=False)
                
                logger.info(f"⏹️ Grabación completada: {self.current_metadata['recording_id']}")
                
                result = self.current_metadata.copy()
                self.current_metadata = None
                self.current_file = None
                return result
        
        except Exception as e:
            logger.error(f"Error deteniendo grabación: {e}")
            self.is_recording = False
        
        return {}
    
    def _recording_thread(self):
        """Thread de grabación de audio"""
        try:
            frames = []
            
            while self.is_recording and self.stream:
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    logger.warning(f"Error leyendo audio: {e}")
                    break
            
            # Guardar archivo WAV
            if self.current_file and frames:
                with wave.open(self.current_file, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(
                        self.pyaudio_instance.get_sample_size(self.audio_format)
                    )
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(b''.join(frames))
        
        except Exception as e:
            logger.error(f"Error en thread de grabación: {e}")
    
    def get_recording_path(self, recording_id: str) -> Optional[str]:
        """Obtener ruta de una grabación"""
        file_path = self.recordings_dir / f"{recording_id}.wav"
        if file_path.exists():
            return str(file_path)
        return None
    
    def get_metadata(self, recording_id: str) -> Optional[Dict]:
        """Obtener metadata de una grabación"""
        metadata_file = self.recordings_dir / f"{recording_id}_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error leyendo metadata: {e}")
        return None
    
    def list_recordings(self, user_id: Optional[str] = None) -> List[Dict]:
        """Listar grabaciones disponibles"""
        recordings = []
        
        for metadata_file in self.recordings_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                    # Filtrar por usuario si se especifica
                    if user_id is None or metadata.get('user_id') == user_id:
                        recordings.append(metadata)
            except Exception as e:
                logger.warning(f"Error leyendo {metadata_file}: {e}")
        
        # Ordenar por fecha descendente
        recordings.sort(
            key=lambda x: x.get('start_time', ''),
            reverse=True
        )
        
        return recordings
    
    def delete_recording(self, recording_id: str) -> bool:
        """Eliminar una grabación"""
        try:
            file_path = self.recordings_dir / f"{recording_id}.wav"
            metadata_file = self.recordings_dir / f"{recording_id}_metadata.json"
            
            if file_path.exists():
                os.remove(file_path)
            if metadata_file.exists():
                os.remove(metadata_file)
            
            logger.info(f"🗑️ Grabación eliminada: {recording_id}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando grabación: {e}")
            return False
    
    def export_recording(self, recording_id: str, export_path: str) -> bool:
        """
        Exportar grabación a ubicación diferente
        
        Args:
            recording_id: ID de grabación
            export_path: Ruta de destino
        
        Returns:
            True si exitoso
        """
        try:
            source_path = self.recordings_dir / f"{recording_id}.wav"
            
            if not source_path.exists():
                logger.error(f"Grabación no encontrada: {recording_id}")
                return False
            
            # Copiar archivo
            import shutil
            shutil.copy2(source_path, export_path)
            
            # Copiar metadata
            metadata = self.get_metadata(recording_id)
            if metadata:
                metadata_path = export_path.replace('.wav', '_metadata.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📤 Grabación exportada: {export_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exportando grabación: {e}")
            return False
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.is_recording:
            self.stop_recording()
        
        if self.stream:
            self.stream.close()
        
        self.pyaudio_instance.terminate()
        logger.info("🧹 CallRecorder limpiado")


# Instancia global
call_recorder: Optional[CallRecorder] = None


def initialize_call_recorder(recordings_dir: str = "recordings") -> CallRecorder:
    """Inicializar grabador de llamadas"""
    global call_recorder
    call_recorder = CallRecorder(recordings_dir)
    return call_recorder


def get_call_recorder() -> Optional[CallRecorder]:
    """Obtener instancia del grabador"""
    global call_recorder
    return call_recorder

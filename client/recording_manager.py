"""
Recording Manager - Sistema Completo de Grabación
CallManager v1.0.1.2

Grabación de audio del sistema y micrófono con metadata automática
Integración con base de datos para auditoría

Autor: CallManager System
Versión: 1.0.1.2
"""

import sounddevice as sd
import soundfile as sf
import json
import os
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class AudioRecorder:
    """
    Grabador de audio profesional con soporte para múltiples fuentes
    
    Características:
    - Captura de micrófono (entrada local)
    - Grabación de audio del sistema (requiere VB-Cable en Windows)
    - Metadata automática (duración, timestamp, participantes)
    - Almacenamiento WAV de alta calidad
    - Interfaz threading para no bloquear UI
    """
    
    def __init__(
        self,
        save_dir: str = "recordings",
        sample_rate: int = 44100,
        channels: int = 1,
        subtype: str = "PCM_16"
    ):
        """
        Inicializar grabador de audio
        
        Args:
            save_dir: Directorio para guardar grabaciones
            sample_rate: Frecuencia de muestreo en Hz (44100, 48000)
            channels: Número de canales (1=mono, 2=estéreo)
            subtype: Formato de audio (PCM_16 recomendado)
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.sample_rate = sample_rate
        self.channels = channels
        self.subtype = subtype
        self.chunk_size = 2048
        
        # Estado de grabación
        self.is_recording = False
        self.recording_data = []
        self.stream = None
        self.recording_thread = None
        self.current_filepath = None
        self.start_time = None
        
        # Metadata
        self.current_metadata = None
        
        logger.info(f"🎙️ AudioRecorder inicializado ({sample_rate}Hz, {channels}ch, {subtype})")
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback para capturar audio en tiempo real"""
        if status:
            logger.warning(f"⚠️ Estado de audio: {status}")
        
        if self.is_recording:
            # Copiar datos para evitar problemas de referencia
            self.recording_data.append(indata.copy())
    
    def start_recording(
        self,
        filename: str,
        contact_name: str = "Unknown",
        contact_phone: str = "",
        user_id: str = "system",
        user_name: str = "System User",
        call_id: str = "",
        device_index: Optional[int] = None
    ) -> str:
        """
        Iniciar grabación de audio
        
        Args:
            filename: Nombre base para el archivo (sin extensión)
            contact_name: Nombre del contacto en la llamada
            contact_phone: Teléfono del contacto
            user_id: ID del usuario que realiza la llamada
            user_name: Nombre del usuario
            call_id: ID de la llamada (para auditoría)
            device_index: Índice del dispositivo de audio (None = default)
            
        Returns:
            Ruta completa del archivo de grabación
        """
        if self.is_recording:
            logger.warning("⚠️ Ya hay una grabación en curso")
            return self.current_filepath
        
        self.is_recording = True
        self.recording_data = []
        self.start_time = datetime.now()
        
        # Construir nombre de archivo único
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.current_filepath = str(
            self.save_dir / f"{filename}_{contact_name}_{timestamp}.wav"
        )
        
        # Crear metadata
        self.current_metadata = {
            "recording_id": f"{call_id}_{timestamp}" if call_id else timestamp,
            "call_id": call_id,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "user_id": user_id,
            "user_name": user_name,
            "start_time": self.start_time.isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "file_path": self.current_filepath,
            "file_size_bytes": 0,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "status": "RECORDING"
        }
        
        try:
            # Usar índice de dispositivo específico si se proporciona
            kwargs = {
                "samplerate": self.sample_rate,
                "channels": self.channels,
                "dtype": "float32",
                "callback": self._audio_callback,
                "blocksize": self.chunk_size
            }
            
            if device_index is not None:
                kwargs["device"] = device_index
            
            # Crear stream de entrada
            self.stream = sd.InputStream(**kwargs)
            self.stream.start()
            
            logger.info(f"🔴 Grabación iniciada: {self.current_filepath}")
            return self.current_filepath
            
        except Exception as e:
            logger.error(f"❌ Error iniciando grabación: {str(e)}")
            self.is_recording = False
            self.current_metadata["status"] = "ERROR"
            return ""
    
    def stop_recording(self) -> Optional[Dict]:
        """
        Detener grabación y guardar archivo
        
        Returns:
            Dictionary con metadata de la grabación o None si hay error
        """
        if not self.is_recording:
            logger.warning("⚠️ No hay grabación activa")
            return None
        
        try:
            self.is_recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Procesar datos grabados
            if self.recording_data:
                # Concatenar buffers de audio
                audio_array = np.concatenate(self.recording_data, axis=0)
                
                # Guardar archivo WAV
                sf.write(
                    self.current_filepath,
                    audio_array,
                    self.sample_rate,
                    subtype=self.subtype
                )
                
                # Actualizar metadata
                end_time = datetime.now()
                duration = (end_time - self.start_time).total_seconds()
                file_size = os.path.getsize(self.current_filepath)
                
                self.current_metadata.update({
                    "end_time": end_time.isoformat(),
                    "duration_seconds": round(duration, 2),
                    "file_size_bytes": file_size,
                    "status": "COMPLETED"
                })
                
                # Guardar metadata en JSON
                metadata_path = self.current_filepath.replace(".wav", "_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_metadata, f, indent=2, ensure_ascii=False)
                
                logger.info(
                    f"✅ Grabación guardada: {self.current_filepath} "
                    f"({duration:.1f}s, {file_size:,} bytes)"
                )
                
                return self.current_metadata
            else:
                logger.warning("⚠️ No se capturó audio")
                self.current_metadata["status"] = "NO_AUDIO"
                return self.current_metadata
                
        except Exception as e:
            logger.error(f"❌ Error guardando grabación: {str(e)}")
            self.current_metadata["status"] = "ERROR"
            return self.current_metadata
    
    def get_recording_path(self) -> Optional[str]:
        """Obtener ruta actual de grabación"""
        return self.current_filepath
    
    def get_metadata(self, filepath: str = None) -> Optional[Dict]:
        """
        Obtener metadata de una grabación
        
        Args:
            filepath: Ruta del archivo (None = actual)
            
        Returns:
            Dictionary con metadata
        """
        if filepath is None:
            return self.current_metadata
        
        try:
            metadata_path = filepath.replace(".wav", "_metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"⚠️ No se encontró metadata para {filepath}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error leyendo metadata: {str(e)}")
            return None
    
    def list_recordings(
        self,
        user_id: str = None,
        contact_name: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Listar grabaciones disponibles
        
        Args:
            user_id: Filtrar por usuario (None = todas)
            contact_name: Filtrar por contacto (None = todas)
            limit: Máximo de registros a retornar
            
        Returns:
            Lista de metadata de grabaciones
        """
        recordings = []
        
        try:
            # Buscar todos los archivos WAV
            for wav_file in sorted(
                self.save_dir.glob("*.wav"),
                reverse=True  # Más recientes primero
            )[:limit]:
                metadata = self.get_metadata(str(wav_file))
                
                if metadata is None:
                    continue
                
                # Aplicar filtros
                if user_id and metadata.get("user_id") != user_id:
                    continue
                
                if contact_name and metadata.get("contact_name") != contact_name:
                    continue
                
                recordings.append(metadata)
            
            logger.info(f"📋 Encontradas {len(recordings)} grabaciones")
            return recordings
            
        except Exception as e:
            logger.error(f"❌ Error listando grabaciones: {str(e)}")
            return []
    
    def delete_recording(self, filepath: str) -> bool:
        """
        Eliminar grabación (archivo + metadata)
        
        Args:
            filepath: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            
            metadata_path = filepath.replace(".wav", "_metadata.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"🗑️ Grabación eliminada: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error eliminando grabación: {str(e)}")
            return False
    
    def export_recording(
        self,
        filepath: str,
        export_path: str
    ) -> bool:
        """
        Exportar grabación a otra ubicación
        
        Args:
            filepath: Ruta fuente
            export_path: Ruta destino (carpeta o archivo completo)
            
        Returns:
            True si se exportó exitosamente
        """
        try:
            import shutil
            
            # Si export_path es directorio, mantener nombre original
            if os.path.isdir(export_path):
                dest = os.path.join(export_path, os.path.basename(filepath))
            else:
                dest = export_path
            
            # Copiar archivo
            shutil.copy2(filepath, dest)
            
            # Copiar metadata
            src_meta = filepath.replace(".wav", "_metadata.json")
            if os.path.exists(src_meta):
                dest_meta = dest.replace(".wav", "_metadata.json")
                shutil.copy2(src_meta, dest_meta)
            
            logger.info(f"📤 Grabación exportada a: {dest}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando grabación: {str(e)}")
            return False
    
    def get_statistics(self, user_id: str = None) -> Dict:
        """
        Obtener estadísticas de grabaciones
        
        Args:
            user_id: Filtrar por usuario
            
        Returns:
            Dictionary con estadísticas
        """
        recordings = self.list_recordings(user_id=user_id)
        
        if not recordings:
            return {
                "total_recordings": 0,
                "total_duration_seconds": 0,
                "total_size_bytes": 0
            }
        
        total_duration = sum(r.get("duration_seconds", 0) for r in recordings)
        total_size = sum(r.get("file_size_bytes", 0) for r in recordings)
        
        return {
            "total_recordings": len(recordings),
            "total_duration_seconds": round(total_duration, 2),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_duration": round(total_duration / len(recordings), 2) if recordings else 0
        }
    
    def list_devices(self) -> List[Dict]:
        """
        Listar dispositivos de audio disponibles
        
        Returns:
            Lista de dispositivos con índice y nombre
        """
        try:
            devices = sd.query_devices()
            
            input_devices = []
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        "index": idx,
                        "name": device['name'],
                        "channels": device['max_input_channels'],
                        "sample_rate": device['default_samplerate']
                    })
            
            return input_devices
            
        except Exception as e:
            logger.error(f"❌ Error listando dispositivos: {str(e)}")
            return []


# Instancia global singleton
_recorder_instance: Optional[AudioRecorder] = None


def initialize_audio_recorder(
    save_dir: str = "recordings",
    sample_rate: int = 44100
) -> AudioRecorder:
    """
    Inicializar AudioRecorder singleton
    
    Args:
        save_dir: Directorio para grabaciones
        sample_rate: Frecuencia de muestreo
        
    Returns:
        Instancia de AudioRecorder
    """
    global _recorder_instance
    
    if _recorder_instance is None:
        _recorder_instance = AudioRecorder(
            save_dir=save_dir,
            sample_rate=sample_rate
        )
    
    return _recorder_instance


def get_audio_recorder() -> Optional[AudioRecorder]:
    """Obtener instancia global de AudioRecorder"""
    global _recorder_instance
    
    if _recorder_instance is None:
        _recorder_instance = AudioRecorder()
    
    return _recorder_instance


if __name__ == "__main__":
    # Test simple
    logging.basicConfig(level=logging.INFO)
    
    recorder = initialize_audio_recorder()
    
    # Listar dispositivos disponibles
    print("🎙️ Dispositivos de audio disponibles:")
    print("=" * 60)
    for device in recorder.list_devices():
        print(f"  [{device['index']}] {device['name']} ({device['channels']}ch, {device['sample_rate']}Hz)")
    
    # Test de grabación corta (5 segundos)
    print("\n🧪 Iniciando grabación de prueba (5 segundos)...")
    filepath = recorder.start_recording(
        filename="test",
        contact_name="John Doe",
        contact_phone="555-1234",
        user_id="test_user",
        user_name="Test User"
    )
    
    import time
    time.sleep(5)
    
    metadata = recorder.stop_recording()
    print(f"✅ Grabación completada!")
    print(f"   Archivo: {metadata['file_path']}")
    print(f"   Duración: {metadata['duration_seconds']}s")
    print(f"   Tamaño: {metadata['file_size_bytes']:,} bytes")

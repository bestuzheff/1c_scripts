import os
import json
import shutil
import zipfile
import logging
from datetime import datetime, timedelta

# Константы
DAYS_TO_KEEP = 20  # Хранить резервные копии 30 дней
CONFIG_FILE = "backup_config.json"  # Путь к файлу конфигурации
LOG_FILE = "backup_log.log"  # Файл для логов

def setup_logging():
    """Настройка логирования в файл"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
        ]
    )

def load_config(config_path):
    """Загрузка конфигурации из JSON файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Ошибка загрузки конфигурации: {str(e)}")
        raise

def cleanup_old_backups(backup_dirs):
    """Удаление старых резервных копий"""
    if DAYS_TO_KEEP <= 0:
        return
    
    cutoff_date = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    
    for backup_dir in backup_dirs:
        if not os.path.exists(backup_dir):
            continue
            
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            if not os.path.isfile(file_path) or not filename.lower().endswith('.zip'):
                continue
                
            try:
                # Разбираем имя файла на части
                parts = filename.split('_')
                if len(parts) < 3:
                    raise ValueError("Недостаточно частей в имени файла")
                
                # Собираем строку с датой (последние 2 части перед .zip)
                date_str = '_'.join(parts[-2:]).replace('.zip', '')
                
                # Пробуем разные форматы даты
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                except ValueError:
                    file_date = datetime.strptime(date_str, "%d-%m-%Y_%H-%M-%S")
                
                if file_date < cutoff_date:
                    os.remove(file_path)
                    logging.info(f"Удален устаревший файл: {file_path}")
                    
            except Exception as e:
                logging.warning(f"Некорректное имя файла {filename}: {str(e)}")
                continue

def get_backup_dir(backup_dirs):
    """Выбор папки для резервной копии на основе четности дня"""
    day = datetime.now().day
    return backup_dirs[0] if day % 2 == 0 else backup_dirs[1]

def create_backup(file_mapping):
    """Создание резервных копий файлов"""
    for file_path, backup_dirs in file_mapping.items():
        if not os.path.exists(file_path):
            logging.warning(f"Файл {file_path} не существует, пропускаем")
            continue
            
        backup_dir = get_backup_dir(backup_dirs)
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = os.path.basename(file_path)
        archive_name = f"{file_name}_{timestamp}.zip"
        archive_path = os.path.join(backup_dir, archive_name)
        
        try:
            temp_path = os.path.join(backup_dir, file_name)
            shutil.copy2(file_path, temp_path)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_path, arcname=file_name)
            
            os.remove(temp_path)
            logging.info(f"Создана резервная копия: {archive_path}")
            
        except Exception as e:
            logging.error(f"Ошибка при создании резервной копии для {file_path}: {str(e)}")
    
    all_backup_dirs = [d for dirs in file_mapping.values() for d in dirs]
    cleanup_old_backups(all_backup_dirs)

def main():
    setup_logging()
    logging.info("=== Запуск процесса резервного копирования ===")
    
    try:
        config = load_config(CONFIG_FILE)
        
        if not isinstance(config, dict):
            logging.error("Конфигурация должна быть словарем")
            return
            
        if not config:
            logging.error("Не указаны файлы для резервного копирования")
            return
            
        file_mapping = {}
        for key, value in config.items():
            if isinstance(value, list) and len(value) == 2:
                file_mapping[key] = value
            else:
                logging.error(f"Для файла {key} должно быть указано 2 папки назначения")
        
        if not file_mapping:
            logging.error("Не найдено корректных путей для резервного копирования")
            return
            
        create_backup(file_mapping)
        
    except FileNotFoundError:
        logging.error(f"Файл конфигурации {CONFIG_FILE} не найден")
    except json.JSONDecodeError as jde:
        logging.error(f"Ошибка чтения JSON: {str(jde)}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")
    finally:
        logging.info("=== Завершение процесса резервного копирования ===\n")

if __name__ == "__main__":
    main()
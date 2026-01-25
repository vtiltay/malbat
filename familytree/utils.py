import os
import shutil
from pathlib import Path
from django.conf import settings


def normalize_gramps_media_path(gramps_path):
    """
    Normalise le chemin d'un fichier média Gramps.
    Retire les chemins absolus et normalise les séparateurs.
    
    Args:
        gramps_path: Chemin du fichier depuis Gramps
        
    Returns:
        Chemin normalisé relatif
    """
    if not gramps_path:
        return None
        
    # Convertir en Path pour normalisation
    path = Path(gramps_path)
    
    # Si c'est un chemin absolu, prendre seulement le nom du fichier
    if path.is_absolute():
        return path.name
    
    # Sinon, normaliser le chemin relatif
    return str(path).replace('\\', '/')


def find_gramps_media_file(gramps_path, gramps_media_root=None):
    """
    Recherche un fichier média dans les dossiers possibles de Gramps.
    
    Args:
        gramps_path: Chemin du fichier depuis Gramps
        gramps_media_root: Dossier racine des médias Gramps (optionnel)
        
    Returns:
        Chemin complet du fichier s'il est trouvé, None sinon
    """
    if not gramps_path:
        return None
    
    # Normaliser le chemin
    normalized_path = normalize_gramps_media_path(gramps_path)
    if not normalized_path:
        return None
    
    # Liste des dossiers où chercher
    search_dirs = []
    
    if gramps_media_root:
        search_dirs.append(Path(gramps_media_root))
    
    # Ajouter le dossier media de Django
    if hasattr(settings, 'MEDIA_ROOT'):
        search_dirs.append(Path(settings.MEDIA_ROOT))
    
    # Chercher dans chaque dossier
    for search_dir in search_dirs:
        # Essayer le chemin complet
        full_path = search_dir / normalized_path
        if full_path.exists() and full_path.is_file():
            return str(full_path)
        
        # Essayer juste le nom du fichier
        file_name = Path(normalized_path).name
        full_path = search_dir / file_name
        if full_path.exists() and full_path.is_file():
            return str(full_path)
    
    return None


def ensure_media_directory_permissions(directory_path):
    """
    S'assure que le dossier média existe et a les bonnes permissions.
    
    Args:
        directory_path: Chemin du dossier à vérifier
        
    Returns:
        True si le dossier existe et est accessible, False sinon
    """
    try:
        directory = Path(directory_path)
        
        # Créer le dossier s'il n'existe pas
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        
        # Vérifier que c'est bien un dossier
        if not directory.is_dir():
            return False
        
        # Tester l'accès en écriture
        test_file = directory / '.permissions_test'
        try:
            test_file.touch()
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False
            
    except Exception:
        return False


def copy_gramps_media_to_django(source_path, relative_dest_path):
    """
    Copie un fichier média de Gramps vers le dossier média de Django.
    
    Args:
        source_path: Chemin complet du fichier source
        relative_dest_path: Chemin relatif de destination dans MEDIA_ROOT
        
    Returns:
        Chemin relatif du fichier copié, ou None en cas d'erreur
    """
    if not source_path or not relative_dest_path:
        return None
    
    try:
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            return None
        
        # Construire le chemin de destination
        dest = Path(settings.MEDIA_ROOT) / relative_dest_path
        
        # S'assurer que le dossier parent existe
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copier le fichier
        shutil.copy2(source, dest)
        
        return relative_dest_path
        
    except Exception as e:
        print(f"Erreur lors de la copie du média: {e}")
        return None

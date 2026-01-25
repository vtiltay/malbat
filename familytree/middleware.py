# familytree/middleware.py
"""
Middleware pour gérer correctement le cache avec les traductions i18n
"""

from django.utils.cache import patch_response_headers, patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class I18nCacheMiddleware(MiddlewareMixin):
    """
    Middleware qui force Django à ne pas mettre en cache les pages multilingues
    Cela évite les problèmes où Chrome garde la version en cache dans une langue
    """
    
    def process_response(self, request, response):
        """
        Ajoute les headers appropriés pour éviter le cache de la langue
        """
        # Ajouter 'Accept-Language' à Vary pour que chaque langue soit cachée séparément
        patch_vary_headers(response, ['Accept-Language', 'Cookie'])
        
        # Force le navigateur à revalider le cache à chaque requête pour les pages avec traductions
        # max_age=0 signifie "cache, mais revalidate immédiatement"
        patch_response_headers(response, cache_timeout=0)
        
        # Headers explicites pour éviter le cache
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response

import { apiService } from './api.js';

export const searchService = {
  /**
   * Realiza busca unificada
   */
  async search(searchRequest) {
    try {
      const response = await apiService.post('/api/v1/search', searchRequest);
      return response;
    } catch (error) {
      console.error('Search failed:', error);
      throw new Error('Falha na busca. Tente novamente.');
    }
  },

  /**
   * Obtém sugestões de busca
   */
  async getSuggestions(query) {
    try {
      const response = await apiService.get('/api/v1/search/suggestions', { q: query });
      return response.suggestions || [];
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      return [];
    }
  },

  /**
   * Verifica status das APIs
   */
  async getApisStatus() {
    try {
      const response = await apiService.get('/api/v1/health/apis');
      return response.apis || [];
    } catch (error) {
      console.error('Failed to get APIs status:', error);
      return [];
    }
  },

  /**
   * Verifica saúde do sistema
   */
  async getHealthCheck() {
    try {
      const response = await apiService.get('/api/v1/health');
      return response;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};


import { useState, useCallback, useRef } from 'react';
import { searchService } from '../services/searchService.js';

export const useSearch = () => {
  const [state, setState] = useState({
    results: [],
    loading: false,
    error: null,
    hasMore: false,
    total: 0,
    page: 1,
    query: '',
    searchTime: 0,
    apisSearched: []
  });

  const abortControllerRef = useRef(null);

  const search = useCallback(async (searchParams, resetResults = true) => {
    // Cancela busca anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Cria novo controller para esta busca
    abortControllerRef.current = new AbortController();

    setState(prev => ({
      ...prev,
      loading: true,
      error: null,
      ...(resetResults && { results: [], page: 1 })
    }));

    try {
      const requestData = {
        query: searchParams.query,
        page: resetResults ? 1 : state.page + 1,
        limit: searchParams.limit || 20,
        ...(searchParams.apis && { apis: searchParams.apis }),
        ...(searchParams.categories && { categories: searchParams.categories }),
        ...(searchParams.dateStart && { date_start: searchParams.dateStart }),
        ...(searchParams.dateEnd && { date_end: searchParams.dateEnd })
      };

      const response = await searchService.search(requestData);

      setState(prev => ({
        ...prev,
        loading: false,
        results: resetResults ? response.results : [...prev.results, ...response.results],
        hasMore: response.has_more,
        total: response.total,
        page: response.page,
        query: response.query,
        searchTime: response.search_time_ms,
        apisSearched: response.apis_searched,
        error: null
      }));

      return response;
    } catch (error) {
      if (error.name !== 'AbortError') {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error.message || 'Erro na busca'
        }));
      }
      throw error;
    }
  }, [state.page]);

  const loadMore = useCallback(async () => {
    if (state.loading || !state.hasMore || !state.query) return;

    try {
      await search({
        query: state.query,
        limit: 20
      }, false);
    } catch (error) {
      console.error('Load more failed:', error);
    }
  }, [search, state.loading, state.hasMore, state.query]);

  const clearResults = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setState({
      results: [],
      loading: false,
      error: null,
      hasMore: false,
      total: 0,
      page: 1,
      query: '',
      searchTime: 0,
      apisSearched: []
    });
  }, []);

  return {
    ...state,
    search,
    loadMore,
    clearResults
  };
};


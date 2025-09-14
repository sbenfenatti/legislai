import React from 'react';
import { Search, AlertCircle, Loader2 } from 'lucide-react';
import ResultCard from './ResultCard.jsx';
import { useInfiniteScroll } from '../../hooks/useInfiniteScroll.js';

const SearchResults = ({ 
  results = [], 
  loading = false, 
  error = null, 
  hasMore = false,
  total = 0,
  query = '',
  searchTime = 0,
  apisSearched = [],
  onLoadMore
}) => {
  const [isFetchingMore] = useInfiniteScroll(onLoadMore, hasMore && !loading);

  // Estado de carregamento inicial
  if (loading && results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-600">Buscando dados oficiais...</p>
        <p className="text-sm text-gray-500 mt-2">
          Consultando {apisSearched.length > 0 ? apisSearched.join(', ') : 'APIs governamentais'}
        </p>
      </div>
    );
  }

  // Estado de erro
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Erro na busca
        </h3>
        <p className="text-gray-600 text-center max-w-md">
          {error}
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Tente novamente ou verifique sua conexão com a internet.
        </p>
      </div>
    );
  }

  // Estado vazio (sem resultados)
  if (!loading && results.length === 0 && query) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Search className="w-12 h-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Nenhum resultado encontrado
        </h3>
        <p className="text-gray-600 text-center max-w-md mb-4">
          Não encontramos resultados para "<strong>{query}</strong>" nas APIs consultadas.
        </p>
        <div className="text-sm text-gray-500 space-y-1">
          <p>Dicas para melhorar sua busca:</p>
          <ul className="list-disc list-inside space-y-1 mt-2">
            <li>Tente termos mais gerais (ex: "educação" ao invés de "educação fundamental")</li>
            <li>Use palavras-chave relacionadas (ex: "despesas", "servidores", "licitações")</li>
            <li>Verifique a ortografia dos termos</li>
            <li>Experimente sinônimos ou termos alternativos</li>
          </ul>
        </div>
      </div>
    );
  }

  // Estado inicial (sem busca realizada)
  if (!query && results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Search className="w-16 h-16 text-gray-300 mb-6" />
        <h3 className="text-xl font-semibold text-gray-900 mb-3">
          Busque dados oficiais do governo
        </h3>
        <p className="text-gray-600 text-center max-w-lg mb-6">
          Digite um termo na barra de busca acima para encontrar informações de transparência, 
          licitações, servidores públicos e muito mais.
        </p>
        
        {/* Sugestões de busca */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-w-4xl">
          {[
            'despesas educação',
            'servidores públicos',
            'licitações obras',
            'bolsa família',
            'contratos governo',
            'viagens oficiais'
          ].map((suggestion) => (
            <div 
              key={suggestion}
              className="px-4 py-2 bg-gray-50 rounded-lg text-sm text-gray-700 text-center border border-gray-200"
            >
              {suggestion}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Resultados encontrados
  return (
    <div className="space-y-6">
      {/* Header dos resultados */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Resultados para "{query}"
          </h2>
          <p className="text-sm text-gray-600">
            {total.toLocaleString()} resultado{total !== 1 ? 's' : ''} encontrado{total !== 1 ? 's' : ''} 
            {searchTime > 0 && ` em ${searchTime}ms`}
          </p>
        </div>
        
        {apisSearched.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Fontes:</span>
            {apisSearched.map((api) => (
              <span 
                key={api}
                className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full border border-blue-200"
              >
                {api.replace('_', ' ')}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Lista de resultados */}
      <div className="space-y-4">
        {results.map((result, index) => (
          <ResultCard 
            key={`${result.id}-${index}`} 
            result={result} 
          />
        ))}
      </div>

      {/* Indicador de carregamento de mais resultados */}
      {(loading || isFetchingMore) && results.length > 0 && (
        <div className="flex justify-center py-8">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
            <span className="text-gray-600">Carregando mais resultados...</span>
          </div>
        </div>
      )}

      {/* Indicador de fim dos resultados */}
      {!hasMore && !loading && results.length > 0 && (
        <div className="flex justify-center py-8">
          <div className="text-center">
            <p className="text-gray-500 mb-2">
              Fim dos resultados
            </p>
            <p className="text-sm text-gray-400">
              Mostrando todos os {results.length} resultado{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchResults;


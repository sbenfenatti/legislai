# Estrutura do Frontend - React

## Visão Geral
Frontend moderno desenvolvido em React com TypeScript, oferecendo interface sóbria e responsiva para busca unificada em dados governamentais brasileiros.

## Estrutura de Diretórios
```
frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
│
├── src/
│   ├── components/           # Componentes reutilizáveis
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.module.css
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   ├── Loading/
│   │   │   └── ErrorBoundary/
│   │   │
│   │   ├── layout/
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   ├── Sidebar/
│   │   │   └── Layout/
│   │   │
│   │   └── search/
│   │       ├── SearchBar/
│   │       ├── SearchFilters/
│   │       ├── SearchResults/
│   │       ├── ResultCard/
│   │       └── InfiniteScroll/
│   │
│   ├── pages/               # Páginas da aplicação
│   │   ├── Home/
│   │   │   ├── Home.tsx
│   │   │   ├── Home.module.css
│   │   │   └── index.ts
│   │   ├── Search/
│   │   ├── About/
│   │   └── NotFound/
│   │
│   ├── hooks/               # Custom hooks
│   │   ├── useSearch.ts
│   │   ├── useInfiniteScroll.ts
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   └── useApi.ts
│   │
│   ├── services/            # Serviços de API
│   │   ├── api.ts           # Configuração base do Axios
│   │   ├── searchService.ts
│   │   ├── apiService.ts
│   │   └── types.ts         # Tipos TypeScript
│   │
│   ├── context/             # Context API
│   │   ├── SearchContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── AppContext.tsx
│   │
│   ├── utils/               # Utilitários
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   │
│   ├── styles/              # Estilos globais
│   │   ├── globals.css
│   │   ├── variables.css
│   │   ├── reset.css
│   │   └── themes.css
│   │
│   ├── assets/              # Assets estáticos
│   │   ├── images/
│   │   ├── icons/
│   │   └── fonts/
│   │
│   ├── App.tsx              # Componente principal
│   ├── App.css
│   ├── index.tsx            # Entry point
│   └── index.css
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Componentes Principais

### 1. SearchBar - Barra de Busca Inteligente
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  suggestions?: string[];
  loading?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = "Buscar dados oficiais...",
  suggestions = [],
  loading = false
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  // Implementação do componente
};
```

### 2. SearchFilters - Filtros Avançados
```typescript
interface FilterOptions {
  apis: string[];
  categories: string[];
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
}

const SearchFilters: React.FC<{
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
}> = ({ filters, onFiltersChange }) => {
  // Implementação dos filtros
};
```

### 3. InfiniteScroll - Rolagem Dinâmica
```typescript
const InfiniteScroll: React.FC<{
  hasMore: boolean;
  loading: boolean;
  onLoadMore: () => void;
  children: React.ReactNode;
}> = ({ hasMore, loading, onLoadMore, children }) => {
  const [isFetching, setIsFetching] = useInfiniteScroll(onLoadMore);

  return (
    <div className="infinite-scroll">
      {children}
      {loading && <LoadingSkeleton />}
      {!hasMore && <div className="end-message">Fim dos resultados</div>}
    </div>
  );
};
```

### 4. ResultCard - Card de Resultado
```typescript
interface SearchResult {
  id: string;
  source: string;
  category: string;
  title: string;
  description: string;
  data: Record<string, any>;
  relevance: number;
  timestamp: string;
}

const ResultCard: React.FC<{
  result: SearchResult;
  onExpand: (id: string) => void;
}> = ({ result, onExpand }) => {
  return (
    <div className="result-card">
      <div className="card-header">
        <span className="source-badge">{result.source}</span>
        <span className="category-tag">{result.category}</span>
      </div>
      <h3 className="card-title">{result.title}</h3>
      <p className="card-description">{result.description}</p>
      <div className="card-footer">
        <span className="timestamp">{formatDate(result.timestamp)}</span>
        <Button onClick={() => onExpand(result.id)}>Ver detalhes</Button>
      </div>
    </div>
  );
};
```

## Custom Hooks

### useSearch - Hook de Busca
```typescript
interface UseSearchReturn {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  search: (query: string, filters?: FilterOptions) => void;
  loadMore: () => void;
  clearResults: () => void;
}

const useSearch = (): UseSearchReturn => {
  const [state, dispatch] = useReducer(searchReducer, initialState);
  
  const search = useCallback(async (query: string, filters?: FilterOptions) => {
    dispatch({ type: 'SEARCH_START' });
    
    try {
      const response = await searchService.search({
        query,
        ...filters,
        page: 1,
        limit: 20
      });
      
      dispatch({ 
        type: 'SEARCH_SUCCESS', 
        payload: response.data 
      });
    } catch (error) {
      dispatch({ 
        type: 'SEARCH_ERROR', 
        payload: error.message 
      });
    }
  }, []);

  const loadMore = useCallback(async () => {
    // Implementação do load more
  }, [state.currentPage, state.query]);

  return {
    results: state.results,
    loading: state.loading,
    error: state.error,
    hasMore: state.hasMore,
    search,
    loadMore,
    clearResults: () => dispatch({ type: 'CLEAR_RESULTS' })
  };
};
```

### useInfiniteScroll - Hook de Rolagem Infinita
```typescript
const useInfiniteScroll = (callback: () => void) => {
  const [isFetching, setIsFetching] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop 
          !== document.documentElement.offsetHeight || isFetching) return;
      setIsFetching(true);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isFetching]);

  useEffect(() => {
    if (!isFetching) return;
    callback();
  }, [isFetching, callback]);

  const setIsFetchingFalse = useCallback(() => {
    setIsFetching(false);
  }, []);

  return [isFetching, setIsFetchingFalse] as const;
};
```

## Serviços de API

### Configuração Base
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    // Adicionar headers, auth, etc.
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Tratamento global de erros
    return Promise.reject(error);
  }
);
```

### Search Service
```typescript
interface SearchRequest {
  query: string;
  apis?: string[];
  categories?: string[];
  date_start?: string;
  date_end?: string;
  page?: number;
  limit?: number;
}

interface SearchResponse {
  results: SearchResult[];
  total: number;
  page: number;
  has_more: boolean;
}

export const searchService = {
  async search(params: SearchRequest): Promise<SearchResponse> {
    const response = await api.post('/api/v1/search', params);
    return response.data;
  },

  async getApis(): Promise<APIInfo[]> {
    const response = await api.get('/api/v1/apis');
    return response.data;
  },

  async getCategories(): Promise<CategoryInfo[]> {
    const response = await api.get('/api/v1/categories');
    return response.data;
  }
};
```

## Context API

### SearchContext
```typescript
interface SearchContextType {
  searchState: SearchState;
  search: (query: string, filters?: FilterOptions) => void;
  loadMore: () => void;
  setFilters: (filters: FilterOptions) => void;
  clearResults: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  const searchHook = useSearch();
  const [filters, setFilters] = useState<FilterOptions>(defaultFilters);

  const contextValue: SearchContextType = {
    searchState: {
      results: searchHook.results,
      loading: searchHook.loading,
      error: searchHook.error,
      hasMore: searchHook.hasMore,
      filters
    },
    search: searchHook.search,
    loadMore: searchHook.loadMore,
    setFilters,
    clearResults: searchHook.clearResults
  };

  return (
    <SearchContext.Provider value={contextValue}>
      {children}
    </SearchContext.Provider>
  );
};
```

## Estilos e Design

### Variáveis CSS
```css
:root {
  /* Cores principais */
  --primary-color: #1e40af;
  --secondary-color: #64748b;
  --accent-color: #059669;
  --background-color: #f8fafc;
  --surface-color: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;

  /* Tipografia */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;

  /* Espaçamento */
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-3: 0.75rem;
  --spacing-4: 1rem;
  --spacing-6: 1.5rem;
  --spacing-8: 2rem;
  --spacing-12: 3rem;

  /* Sombras */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* Bordas */
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.375rem;
  --border-radius-lg: 0.5rem;
  --border-radius-xl: 0.75rem;
}
```

### Responsividade
```css
/* Mobile First */
.container {
  width: 100%;
  padding: 0 var(--spacing-4);
  margin: 0 auto;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 768px;
    padding: 0 var(--spacing-6);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding: 0 var(--spacing-8);
  }
}

/* Large Desktop */
@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}
```

## Performance e Otimizações

### Code Splitting
```typescript
// Lazy loading de páginas
const Home = lazy(() => import('./pages/Home'));
const Search = lazy(() => import('./pages/Search'));
const About = lazy(() => import('./pages/About'));

// Lazy loading de componentes pesados
const DataVisualization = lazy(() => import('./components/DataVisualization'));
```

### Memoização
```typescript
// Memoização de componentes
const ResultCard = memo(({ result, onExpand }: ResultCardProps) => {
  // Implementação
});

// Memoização de valores computados
const filteredResults = useMemo(() => {
  return results.filter(result => 
    result.category.includes(selectedCategory)
  );
}, [results, selectedCategory]);
```

### Service Worker
```typescript
// Registro do service worker para cache
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}
```

## Testes

### Configuração Jest
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchProvider } from '../context/SearchContext';
import SearchBar from '../components/search/SearchBar';

const renderWithProvider = (component: React.ReactElement) => {
  return render(
    <SearchProvider>
      {component}
    </SearchProvider>
  );
};

test('should perform search when enter is pressed', async () => {
  const mockSearch = jest.fn();
  
  renderWithProvider(
    <SearchBar onSearch={mockSearch} />
  );

  const input = screen.getByPlaceholderText('Buscar dados oficiais...');
  fireEvent.change(input, { target: { value: 'despesas' } });
  fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });

  await waitFor(() => {
    expect(mockSearch).toHaveBeenCalledWith('despesas');
  });
});
```

## Build e Deploy

### Vite Configuration
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['axios', 'date-fns']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

## Vantagens da Arquitetura

1. **Modularidade**: Componentes bem organizados e reutilizáveis
2. **TypeScript**: Tipagem forte para melhor DX e menos bugs
3. **Performance**: Code splitting, lazy loading e memoização
4. **Responsividade**: Design mobile-first
5. **Acessibilidade**: Componentes acessíveis por padrão
6. **Testabilidade**: Arquitetura que facilita testes
7. **Manutenibilidade**: Código limpo e bem estruturado


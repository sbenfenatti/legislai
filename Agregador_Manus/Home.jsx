import React, { useState } from 'react';
import { Database, Shield, Zap, Globe, Info, X } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog.jsx';
import SearchBar from '../components/search/SearchBar.jsx';
import SearchResults from '../components/search/SearchResults.jsx';
import { useSearch } from '../hooks/useSearch.js';
import { useSearchContext } from '../context/SearchContext.jsx';

const Home = () => {
  const [showAbout, setShowAbout] = useState(false);
  const { 
    results, 
    loading, 
    error, 
    hasMore, 
    total, 
    query, 
    searchTime, 
    apisSearched,
    search, 
    loadMore 
  } = useSearch();
  
  const { filters } = useSearchContext();

  const handleSearch = async (searchQuery) => {
    try {
      await search({
        query: searchQuery,
        ...filters
      });
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const features = [
    {
      icon: Database,
      title: 'Dados Oficiais',
      description: 'Acesso direto às APIs oficiais do governo brasileiro com informações sempre atualizadas.'
    },
    {
      icon: Shield,
      title: 'Transparência',
      description: 'Informações de despesas públicas, licitações, contratos e servidores em um só lugar.'
    },
    {
      icon: Zap,
      title: 'Busca Rápida',
      description: 'Sistema otimizado com cache inteligente para consultas rápidas e eficientes.'
    },
    {
      icon: Globe,
      title: 'Múltiplas Fontes',
      description: 'Integração com Portal da Transparência, Câmara, Senado, IBGE e Banco Central.'
    }
  ];

  const stats = [
    { label: 'APIs Integradas', value: '6+' },
    { label: 'Endpoints Disponíveis', value: '80+' },
    { label: 'Categorias de Dados', value: '15+' },
    { label: 'Atualizações', value: 'Tempo Real' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24">
          {/* Header com botão sobre */}
          <div className="flex justify-end mb-8">
            <Button
              variant="outline"
              onClick={() => setShowAbout(true)}
              className="bg-white/80 backdrop-blur-sm"
            >
              <Info className="w-4 h-4 mr-2" />
              Sobre o Sistema
            </Button>
          </div>

          <div className="text-center mb-16">
            <div className="flex justify-center mb-6">
              <div className="flex items-center justify-center w-20 h-20 bg-blue-600 rounded-2xl shadow-lg">
                <Database className="w-10 h-10 text-white" />
              </div>
            </div>
            
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Sistema de Busca
              <span className="block text-blue-600">APIs Oficiais BR</span>
            </h1>
            
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12">
              Acesse dados oficiais do governo brasileiro de forma unificada. 
              Transparência, licitações, servidores públicos e muito mais em uma única plataforma.
            </p>

            {/* Barra de busca principal */}
            <div className="mb-16">
              <SearchBar onSearch={handleSearch} loading={loading} />
            </div>

            {/* Estatísticas */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-600">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Resultados da busca */}
          <SearchResults
            results={results}
            loading={loading}
            error={error}
            hasMore={hasMore}
            total={total}
            query={query}
            searchTime={searchTime}
            apisSearched={apisSearched}
            onLoadMore={loadMore}
          />

          {/* Features (só mostra se não há busca ativa) */}
          {!query && results.length === 0 && (
            <div className="mt-24">
              <div className="text-center mb-16">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Por que usar nosso sistema?
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Uma plataforma moderna e eficiente para acessar dados públicos brasileiros
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {features.map((feature, index) => (
                  <div 
                    key={index}
                    className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                      <feature.icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {feature.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal Sobre */}
      <Dialog open={showAbout} onOpenChange={setShowAbout}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Database className="w-6 h-6 mr-2 text-blue-600" />
              Sobre o Sistema de Busca
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">O que é?</h3>
              <p className="text-gray-600">
                O Sistema de Busca - APIs Oficiais BR é uma plataforma unificada que permite 
                acessar dados oficiais do governo brasileiro de forma rápida e eficiente. 
                Integramos múltiplas APIs governamentais em uma única interface moderna e intuitiva.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">APIs Integradas</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• <strong>Portal da Transparência:</strong> Despesas, servidores, licitações, benefícios sociais</li>
                <li>• <strong>Câmara dos Deputados:</strong> Deputados, proposições, votações</li>
                <li>• <strong>Senado Federal:</strong> Senadores, matérias legislativas</li>
                <li>• <strong>IBGE:</strong> Dados geográficos e demográficos</li>
                <li>• <strong>Banco Central:</strong> Cotações e dados financeiros</li>
                <li>• <strong>Brasil API:</strong> CEP, CNPJ, bancos, municípios</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Funcionalidades</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Busca unificada em múltiplas fontes oficiais</li>
                <li>• Interface responsiva e moderna</li>
                <li>• Rolagem dinâmica para grandes volumes de dados</li>
                <li>• Cache inteligente para performance otimizada</li>
                <li>• Histórico de buscas e sugestões automáticas</li>
                <li>• Exportação de dados em múltiplos formatos</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Tecnologia</h3>
              <p className="text-gray-600">
                Desenvolvido com tecnologias modernas: React para o frontend, 
                FastAPI para o backend, Redis para cache e Docker para deployment. 
                Código aberto e transparente, seguindo as melhores práticas de desenvolvimento.
              </p>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-gray-500 text-center">
                Sistema desenvolvido para promover transparência e facilitar o acesso 
                à informação pública no Brasil.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Home;


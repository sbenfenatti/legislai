import React, { useState } from 'react';
import { 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  Calendar, 
  Database,
  Star,
  Copy,
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Badge } from '@/components/ui/badge.jsx';

const ResultCard = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const getSourceColor = (source) => {
    const colors = {
      'Portal da Transparência': 'bg-blue-100 text-blue-800',
      'Brasil API': 'bg-green-100 text-green-800',
      'Câmara dos Deputados': 'bg-purple-100 text-purple-800',
      'Senado Federal': 'bg-indigo-100 text-indigo-800',
      'IBGE': 'bg-orange-100 text-orange-800',
      'Banco Central': 'bg-red-100 text-red-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const getCategoryColor = (category) => {
    const colors = {
      'despesas': 'bg-red-50 text-red-700 border-red-200',
      'servidores': 'bg-blue-50 text-blue-700 border-blue-200',
      'licitacoes': 'bg-green-50 text-green-700 border-green-200',
      'contratos': 'bg-purple-50 text-purple-700 border-purple-200',
      'beneficios_sociais': 'bg-yellow-50 text-yellow-700 border-yellow-200',
      'viagens': 'bg-indigo-50 text-indigo-700 border-indigo-200',
      'sancoes': 'bg-orange-50 text-orange-700 border-orange-200'
    };
    return colors[category] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const copyToClipboard = async () => {
    try {
      const textToCopy = `${result.title}\n${result.description}\nFonte: ${result.source}\nData: ${formatDate(result.timestamp)}`;
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const renderDataPreview = () => {
    if (!result.data || typeof result.data !== 'object') return null;

    const entries = Object.entries(result.data).slice(0, 5);
    
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
          <Database className="w-4 h-4 mr-2" />
          Dados Disponíveis
        </h4>
        <div className="space-y-2">
          {entries.map(([key, value]) => (
            <div key={key} className="flex justify-between items-start text-sm">
              <span className="font-medium text-gray-600 capitalize">
                {key.replace(/([A-Z])/g, ' $1').toLowerCase()}:
              </span>
              <span className="text-gray-900 text-right max-w-xs truncate">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
          {Object.keys(result.data).length > 5 && (
            <div className="text-xs text-gray-500 italic">
              +{Object.keys(result.data).length - 5} campos adicionais
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
      {/* Header do card */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2 flex-wrap">
            <Badge className={getSourceColor(result.source)}>
              {result.source}
            </Badge>
            <Badge 
              variant="outline" 
              className={getCategoryColor(result.category)}
            >
              {result.category.replace('_', ' ')}
            </Badge>
            {result.relevance > 0.8 && (
              <Badge className="bg-yellow-100 text-yellow-800">
                <Star className="w-3 h-3 mr-1" />
                Alta relevância
              </Badge>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={copyToClipboard}
              className="text-gray-400 hover:text-gray-600"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
            
            {result.url && (
              <Button
                variant="ghost"
                size="sm"
                asChild
              >
                <a 
                  href={result.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-gray-600"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </Button>
            )}
          </div>
        </div>

        {/* Título e descrição */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {result.title}
        </h3>
        
        <p className="text-gray-600 mb-4 line-clamp-3">
          {result.description}
        </p>

        {/* Footer do card */}
        <div className="flex items-center justify-between">
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="w-4 h-4 mr-1" />
            {formatDate(result.timestamp)}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 hover:text-blue-700"
          >
            {isExpanded ? (
              <>
                Menos detalhes
                <ChevronUp className="w-4 h-4 ml-1" />
              </>
            ) : (
              <>
                Mais detalhes
                <ChevronDown className="w-4 h-4 ml-1" />
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Seção expandida */}
      {isExpanded && (
        <div className="border-t border-gray-200 px-6 pb-6">
          {renderDataPreview()}
          
          {/* Métricas */}
          <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
            <span>ID: {result.id}</span>
            <span>Relevância: {Math.round(result.relevance * 100)}%</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;


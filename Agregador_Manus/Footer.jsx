import React from 'react';
import { ExternalLink, Github, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Sobre o projeto */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Sistema de Busca
            </h3>
            <p className="text-sm text-gray-600 mb-3">
              Plataforma unificada para busca em dados oficiais do governo brasileiro.
              Acesse informações de transparência, licitações, servidores e muito mais.
            </p>
            <div className="flex items-center text-sm text-gray-500">
              <Heart className="w-4 h-4 mr-1 text-red-500" />
              Feito com dedicação para o Brasil
            </div>
          </div>

          {/* APIs integradas */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              APIs Integradas
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a 
                  href="https://portaldatransparencia.gov.br" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Portal da Transparência
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a 
                  href="https://dadosabertos.camara.leg.br" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Câmara dos Deputados
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a 
                  href="https://legis.senado.leg.br/dadosabertos" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Senado Federal
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a 
                  href="https://servicodados.ibge.gov.br" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  IBGE
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
            </ul>
          </div>

          {/* Links úteis */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Links Úteis
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a 
                  href="http://localhost:8000/docs" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Documentação da API
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a 
                  href="http://localhost:8000/health" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Status do Sistema
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
              <li>
                <a 
                  href="https://www.gov.br/acessoainformacao" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="hover:text-blue-600 flex items-center"
                >
                  Lei de Acesso à Informação
                  <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2024 Sistema de Busca - APIs Oficiais BR. 
              Dados fornecidos pelos órgãos oficiais do governo brasileiro.
            </p>
            <div className="mt-4 md:mt-0 flex items-center space-x-4">
              <span className="text-xs text-gray-400">
                Versão 1.0.0
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;


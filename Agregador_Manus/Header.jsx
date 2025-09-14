import React from 'react';
import { Search, Database, Info } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';

const Header = ({ onAboutClick }) => {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e título */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Sistema de Busca
              </h1>
              <p className="text-sm text-gray-600">
                APIs Oficiais do Governo Brasileiro
              </p>
            </div>
          </div>

          {/* Navegação */}
          <nav className="hidden md:flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={onAboutClick}
              className="text-gray-600 hover:text-gray-900"
            >
              <Info className="w-4 h-4 mr-2" />
              Sobre
            </Button>
            <Button
              variant="ghost"
              size="sm"
              asChild
            >
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900"
              >
                <Search className="w-4 h-4 mr-2" />
                API Docs
              </a>
            </Button>
          </nav>

          {/* Menu mobile */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={onAboutClick}
            >
              <Info className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;


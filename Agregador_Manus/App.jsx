import React from 'react';
import { SearchProvider } from './context/SearchContext.jsx';
import Header from './components/layout/Header.jsx';
import Footer from './components/layout/Footer.jsx';
import Home from './pages/Home.jsx';
import './App.css';

function App() {
  return (
    <SearchProvider>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Home />
        <Footer />
      </div>
    </SearchProvider>
  );
}

export default App;


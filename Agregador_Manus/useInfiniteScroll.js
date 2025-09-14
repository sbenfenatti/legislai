import { useState, useEffect, useCallback } from 'react';

export const useInfiniteScroll = (callback, hasMore = true) => {
  const [isFetching, setIsFetching] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop 
          >= document.documentElement.offsetHeight - 1000 || isFetching || !hasMore) {
        return;
      }
      setIsFetching(true);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isFetching, hasMore]);

  useEffect(() => {
    if (!isFetching) return;
    
    const fetchData = async () => {
      try {
        await callback();
      } catch (error) {
        console.error('Infinite scroll callback failed:', error);
      } finally {
        setIsFetching(false);
      }
    };

    fetchData();
  }, [isFetching, callback]);

  const resetFetching = useCallback(() => {
    setIsFetching(false);
  }, []);

  return [isFetching, resetFetching];
};


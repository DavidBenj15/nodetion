import React, { useState } from 'react';
import { Input, Button, Flex } from '@chakra-ui/react';
import { searchDocuments } from '../../../../../api/search';

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const results = await searchDocuments(query);
      console.log('Search results:', results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ width: '100%' }}>
      <Flex gap={2}>
        <Input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search..."
          disabled={loading}
        />
        <Button type="submit" colorScheme="blue">
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </Flex>
    </form>
  );
};

export default SearchBar;

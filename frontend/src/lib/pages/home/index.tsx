import { Flex, Text } from '@chakra-ui/react';
import SearchBar from './components/SearchBar';

const Home = () => {
  return (
    <Flex
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100%"
      gap={4}
    >
      <Text textStyle="2xl">What's on your mind?</Text>
      <SearchBar />
    </Flex>
  );
};

export default Home;

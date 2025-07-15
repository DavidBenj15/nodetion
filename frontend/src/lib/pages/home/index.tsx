import { Grid } from '@chakra-ui/react';
import SearchBar from './components/SearchBar';

const Home = () => {
  return (
    <Grid gap={4}>
      <SearchBar />
    </Grid>
  );
};

export default Home;

import { Box, Flex } from '@chakra-ui/react';
import type { ReactNode } from 'react';
import { Meta } from './components/meta';
import Navbar from '../../components/ui/navbar';

type LayoutProps = {
  children: ReactNode;
};

export const Layout = ({ children }: LayoutProps) => {
  return (
    <Box margin="0 auto" maxWidth={800} transition="0.5s ease-out">
      <Meta />
      <Navbar />
      <Flex wrap="wrap" margin="8" minHeight="90vh">
        
        <Box width="full" as="main" marginY={22}>
          {children}
        </Box>
      </Flex>
    </Box>
  );
};

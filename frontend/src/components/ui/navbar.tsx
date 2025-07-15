import { Box, Flex, Text } from '@chakra-ui/react';

const Navbar = () => {
  return (
    <Box boxShadow="md" px={4} py={2} bg="white" position="sticky" top={0} zIndex={10}>
      <Flex align="center" justify="space-between">
        <Text fontWeight="bold" fontSize="xl" letterSpacing="wide">
          nodetion
        </Text>
      </Flex>
    </Box>
  );
};

export default Navbar;

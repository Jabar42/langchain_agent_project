import React from 'react';
import { Box, Container, Heading } from '@chakra-ui/react';

function App() {
  return (
    <Container maxW="container.xl" py={8}>
      <Box textAlign="center" py={10}>
        <Heading as="h1" size="2xl">
          AI Agent Platform
        </Heading>
      </Box>
    </Container>
  );
}

export default App; 
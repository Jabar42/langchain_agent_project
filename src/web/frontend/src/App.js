import React from 'react';
import { Box, Container, Heading, Spinner, Center } from '@chakra-ui/react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Auth } from './pages/Auth';

const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!user) {
    return <Auth />;
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Box textAlign="center" py={10}>
        <Heading as="h1" size="2xl">
          Bienvenido, {user.username}
        </Heading>
      </Box>
    </Container>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App; 
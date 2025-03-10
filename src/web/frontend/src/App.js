import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  GridItem,
  Heading,
  Spinner,
  Center,
  Button,
  Flex,
} from '@chakra-ui/react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Auth } from './pages/Auth';
import { Chat } from './components/Chat';
import { ChatList } from './components/ChatList';

const AppContent = () => {
  const { user, loading, logout } = useAuth();
  const [selectedChat, setSelectedChat] = useState(null);

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
    <Container maxW="container.xl" py={4}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading as="h1" size="lg">
          AI Agent Platform
        </Heading>
        <Button onClick={logout} colorScheme="red" variant="outline">
          Cerrar sesión
        </Button>
      </Flex>
      <Grid templateColumns="300px 1fr" gap={4} h="calc(100vh - 100px)">
        <GridItem borderWidth={1} borderRadius="lg" p={4}>
          <ChatList onSelectChat={setSelectedChat} />
        </GridItem>
        <GridItem borderWidth={1} borderRadius="lg" p={4}>
          {selectedChat ? (
            <Chat chatId={selectedChat.id} title={selectedChat.title} />
          ) : (
            <Center h="full">
              <Box textAlign="center">
                <Heading size="md" color="gray.500">
                  Selecciona o crea un chat para comenzar
                </Heading>
              </Box>
            </Center>
          )}
        </GridItem>
      </Grid>
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
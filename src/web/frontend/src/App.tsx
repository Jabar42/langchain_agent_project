import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Box,
  VStack,
  Grid,
  theme,
  Container,
  Heading,
} from '@chakra-ui/react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';

// Componentes
import { Navigation } from './components/Navigation';
import { Chat } from './components/Chat';
import { ModelComparison } from './components/ModelComparison';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { PrivateRoute } from './components/PrivateRoute';

// Contexto de autenticación
import { AuthProvider } from './context/AuthContext';

const queryClient = new QueryClient();

export const App: React.FC = () => {
  return (
    <ChakraProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <Box textAlign="center" fontSize="xl">
              <Grid minH="100vh" p={3}>
                <VStack spacing={8}>
                  <Navigation />
                  <Container maxW="container.xl">
                    <Routes>
                      <Route path="/login" element={<Login />} />
                      <Route
                        path="/"
                        element={
                          <PrivateRoute>
                            <Dashboard />
                          </PrivateRoute>
                        }
                      />
                      <Route
                        path="/chat"
                        element={
                          <PrivateRoute>
                            <Chat />
                          </PrivateRoute>
                        }
                      />
                      <Route
                        path="/compare"
                        element={
                          <PrivateRoute>
                            <ModelComparison />
                          </PrivateRoute>
                        }
                      />
                    </Routes>
                  </Container>
                </VStack>
              </Grid>
            </Box>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
    </ChakraProvider>
  );
}; 
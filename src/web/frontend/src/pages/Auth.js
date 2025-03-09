import React, { useState } from 'react';
import { Container, Center, useColorModeValue } from '@chakra-ui/react';
import { Login } from '../components/Login';
import { Register } from '../components/Register';

export const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const bg = useColorModeValue('gray.50', 'gray.800');

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  return (
    <Container maxW="container.xl" py={20}>
      <Center minH="60vh" bg={bg}>
        {isLogin ? (
          <Login onToggleMode={toggleMode} />
        ) : (
          <Register onToggleMode={toggleMode} />
        )}
      </Center>
    </Container>
  );
}; 
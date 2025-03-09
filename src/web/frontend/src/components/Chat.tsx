import React, { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  useToast,
  Container,
  Select,
  HStack,
} from '@chakra-ui/react';
import { useQuery } from 'react-query';

interface Message {
  text: string;
  isUser: boolean;
  model?: string;
  timestamp: Date;
}

export const Chat: React.FC = () => {
  const [message, setMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  // Obtener lista de modelos disponibles
  const { data: models } = useQuery('models', async () => {
    const response = await fetch('http://localhost:8000/models', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) throw new Error('Failed to fetch models');
    return response.json();
  });

  const handleSend = async () => {
    if (!message.trim()) return;

    setIsLoading(true);
    const userMessage: Message = {
      text: message,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          text: message,
          models: selectedModel ? [selectedModel] : undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const botMessage: Message = {
        text: data.best_response,
        isUser: false,
        model: data.model,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setMessage('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo obtener una respuesta',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="container.lg">
      <VStack spacing={4} align="stretch" h="80vh">
        <Box flex={1} overflowY="auto" p={4} borderWidth={1} borderRadius="md">
          {messages.map((msg, index) => (
            <Box
              key={index}
              bg={msg.isUser ? 'blue.100' : 'gray.100'}
              p={3}
              borderRadius="md"
              mb={2}
              maxW="80%"
              ml={msg.isUser ? 'auto' : 0}
            >
              <Text>{msg.text}</Text>
              {msg.model && (
                <Text fontSize="xs" color="gray.500">
                  Modelo: {msg.model}
                </Text>
              )}
              <Text fontSize="xs" color="gray.500">
                {msg.timestamp.toLocaleTimeString()}
              </Text>
            </Box>
          ))}
        </Box>
        <HStack>
          <Select
            placeholder="Seleccionar modelo"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            {models?.models?.map((model: string) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </Select>
          <Input
            placeholder="Escribe un mensaje..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button
            colorScheme="blue"
            onClick={handleSend}
            isLoading={isLoading}
            loadingText="Enviando..."
          >
            Enviar
          </Button>
        </HStack>
      </VStack>
    </Container>
  );
}; 
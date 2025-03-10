import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  useToast,
  Flex,
  IconButton,
  Heading,
} from '@chakra-ui/react';
import { ArrowUpIcon } from '@chakra-ui/icons';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const Message = ({ content, role }) => (
  <Box
    bg={role === 'user' ? 'blue.50' : 'gray.50'}
    p={3}
    borderRadius="md"
    maxW="80%"
    alignSelf={role === 'user' ? 'flex-end' : 'flex-start'}
    mb={2}
  >
    <Text>{content}</Text>
  </Box>
);

export const Chat = ({ chatId, title }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const toast = useToast();
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/chats/${chatId}/messages/`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setMessages(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los mensajes',
        status: 'error',
        duration: 3000,
      });
    }
  };

  useEffect(() => {
    if (chatId) {
      fetchMessages();
    }
  }, [chatId, fetchMessages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `http://localhost:8000/chats/${chatId}/messages/`,
        {
          content: newMessage,
          role: 'user'
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setMessages(prev => [...prev, response.data.user_message, response.data.assistant_message]);
      setNewMessage('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo enviar el mensaje',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <VStack h="full" spacing={4}>
      <Heading size="md">{title}</Heading>
      <Box
        flex={1}
        w="full"
        overflowY="auto"
        p={4}
        borderWidth={1}
        borderRadius="md"
      >
        <VStack spacing={4} align="stretch">
          {messages.map((message) => (
            <Message
              key={message.id}
              content={message.content}
              role={message.role}
            />
          ))}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      <form onSubmit={handleSendMessage} style={{ width: '100%' }}>
        <Flex>
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Escribe un mensaje..."
            mr={2}
          />
          <IconButton
            type="submit"
            colorScheme="blue"
            aria-label="Enviar mensaje"
            icon={<ArrowUpIcon />}
            isLoading={loading}
          />
        </Flex>
      </form>
    </VStack>
  );
}; 
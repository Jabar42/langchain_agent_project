import React, { useState, useEffect, useCallback } from 'react';
import {
  VStack,
  Button,
  Text,
  useToast,
  Input,
  IconButton,
  HStack,
  Box,
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import axios from 'axios';

export const ChatList = ({ onSelectChat }) => {
  const [chats, setChats] = useState([]);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const fetchChats = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/chats/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setChats(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los chats',
        status: 'error',
        duration: 3000,
      });
    }
  }, [toast]);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleCreateChat = async (e) => {
    e.preventDefault();
    if (!newChatTitle.trim()) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/chats/',
        { title: newChatTitle },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setChats(prev => [...prev, response.data]);
      setNewChatTitle('');
      onSelectChat(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo crear el chat',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <VStack spacing={4} align="stretch" w="full">
      <form onSubmit={handleCreateChat}>
        <HStack>
          <Input
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
            placeholder="Nuevo chat..."
          />
          <IconButton
            type="submit"
            colorScheme="blue"
            aria-label="Crear chat"
            icon={<AddIcon />}
            isLoading={loading}
          />
        </HStack>
      </form>
      <VStack spacing={2} align="stretch">
        {chats.map((chat) => (
          <Button
            key={chat.id}
            onClick={() => onSelectChat(chat)}
            variant="ghost"
            justifyContent="flex-start"
            h="auto"
            py={2}
          >
            <Box>
              <Text fontWeight="bold" isTruncated>
                {chat.title}
              </Text>
              <Text fontSize="sm" color="gray.500">
                {new Date(chat.created_at).toLocaleDateString()}
              </Text>
            </Box>
          </Button>
        ))}
      </VStack>
    </VStack>
  );
}; 
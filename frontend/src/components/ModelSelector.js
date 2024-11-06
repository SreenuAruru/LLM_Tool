import React, { useState } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, TextField, Button } from '@mui/material';

const ModelSelector = ({ setSelectedModel, setApiKey }) => {
  const [apiInput, setApiInput] = useState(""); // API key controlled state
  const [model, setModel] = useState(""); // Model controlled state to avoid undefined issues
  const [showApiKeyInput, setShowApiKeyInput] = useState(false);

  const handleModelChange = (event) => {
    const selectedModel = event.target.value;
    setModel(selectedModel);
    setSelectedModel(selectedModel); // Pass selected model to parent
    setShowApiKeyInput(true); // Show API key input when model is selected
  };

  const handleApiKeyChange = () => {
    setApiKey(apiInput); // Set API key in parent component
    alert(`API Key for ${model} submitted: ${apiInput}`);
  };

  return (
    <Box sx={{ mb: 4 }}>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select AI Model</InputLabel>
        <Select
          value={model} // Ensure value is set to avoid uncontrolled issues
          label="Select AI Model"
          onChange={handleModelChange}
        >
          <MenuItem value="ChatGPT">ChatGPT</MenuItem>
          <MenuItem value="GoogleGemini">Google Gemini</MenuItem>
        </Select>
      </FormControl>

      {showApiKeyInput && (
        <Box>
          <TextField
            fullWidth
            label="Enter API Key"
            value={apiInput} // Controlled value
            onChange={(e) => setApiInput(e.target.value)} // Update API key state
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handleApiKeyChange}>
            Submit API Key
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ModelSelector;

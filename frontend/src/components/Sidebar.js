import React, { useState, useEffect } from "react";
import {
  Drawer,
  List,
  ListItem,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Typography,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from "@mui/material";
import { toast } from "react-toastify";
import axios from "axios";
import { saveStoreId, getStoreId } from "./IndexedDbUtils";

const Sidebar = ({ setSelectedModel, setApiKey, setStoreId }) => {
  const [apiInput, setApiInput] = useState("");
  const [model, setModel] = useState("");
  const [selectModel, setSelectModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false); // State for dialog visibility

  useEffect(() => {
    async function loadStoreId() {
      try {
        const savedStoreId = await getStoreId();
        if (savedStoreId) {
          setStoreId(savedStoreId);
          toast.success("Store ID loaded from IndexedDB.");
        }
      } catch (error) {
        console.error("Error loading Store ID:", error);
      }
    }

    loadStoreId();
  }, [setStoreId]);

  const handleModelChange = (event) => {
    setModel(event.target.value);
    console.log("handleModelChange", event.target.value);
  };

  const selectHandleModelChange = (event) => {
    const selectedModel = event.target.value;
    setSelectModel(selectedModel);
    setSelectedModel(selectedModel);

    const selectedApiModel = availableModels.find(
      (item) => item.ai_model === selectedModel
    );
    if (selectedApiModel) {
      setApiKey(selectedApiModel.api_key_model); // Set the API key dynamically based on the selected model
      console.log(
        "selectedApiModel.api_key_model",
        selectedApiModel.api_key_model
      );
    }
  };

  const handleApiKeyChange = () => {
    // const selectedApiModel = availableModels.find(
    //   (item) => item.ai_model === selectModel
    // );

    // if (selectedApiModel) {
    //   setApiKey(selectedApiModel.api_key_model); // Set the API key dynamically based on the selected model
    // }

    if (apiInput) {
      axios
        .post("http://localhost:8000/store-model-selection/", {
          ai_model: model,
          api_key_model: apiInput,
        })
        .then((response) => {
          console.log(response.data.message);
        })
        .catch((error) => {
          console.error("Error storing model selection:", error);
          toast.error("Error storing model selection");
        });
      toast.success("API Key submitted!");
      setDialogOpen(false); // Close the dialog after submission
    }
  };

  useEffect(() => {
    // Fetch model selection from MySQL via FastAPI
    axios
      .get("http://localhost:8000/fetch-model-selection/")
      .then((response) => {
        const modelSelections = response.data.model_selections;
        if (modelSelections && modelSelections.length > 0) {
          setAvailableModels(modelSelections);
        }
      })
      .catch((error) => {
        console.error("Error fetching model selection:", error);
        toast.error("Error fetching model selection");
      });
  }, [setSelectedModel]);

  const handleFolderUpload = async (event) => {
    const folderFiles = Array.from(event.target.files);
    const formData = new FormData();
    folderFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      setLoading(true);
      const response = await axios.post(
        "http://localhost:8000/process-pdfs/",
        formData
      );
      const storeId = response.data.store_id;
      setStoreId(storeId);
      await saveStoreId(storeId);
      toast.success(response.data.message);
    } catch (error) {
      console.error("Error uploading PDFs:", error);
      toast.error("Error uploading PDFs");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Drawer
      variant="permanent"
      anchor="left"
      sx={{
        width: 240,
        flexShrink: 0,
        "& .MuiDrawer-paper": { width: 240, boxSizing: "border-box" },
      }}
    >
      <List>
        <ListItem>
          <Typography variant="h6" noWrap>
            Options
          </Typography>
        </ListItem>
        <ListItem>
          <Button variant="contained" component="label" sx={{ width: "100%" }}>
            Upload Folders
            <input
              type="file"
              webkitdirectory="true"
              directory="true"
              multiple
              hidden
              onChange={handleFolderUpload}
            />
          </Button>
        </ListItem>
        {loading && (
          <ListItem>
            <CircularProgress />
          </ListItem>
        )}
        {/* Button to open the dialog for adding API key */}
        <ListItem>
          <Button
            variant="contained"
            onClick={() => setDialogOpen(true)}
            fullWidth
          >
            ADD API KEY
          </Button>
        </ListItem>
        <ListItem>
          <FormControl fullWidth>
            <InputLabel>AI Model</InputLabel>
            <Select
              label="AI Model"
              value={selectModel}
              onChange={selectHandleModelChange}
            >
              <MenuItem value="Select Model2">Select Model</MenuItem>
              {availableModels.map(({ ai_model }, index) => (
                <MenuItem key={index} value={ai_model}>
                  {ai_model && typeof ai_model === "string"
                    ? ai_model
                    : "Invalid Model"}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </ListItem>
      </List>

      {/* Dialog for API Key input */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Add API Key</DialogTitle>
        <DialogContent>
          <ListItem>
            <FormControl fullWidth>
              <InputLabel>Select AI Model</InputLabel>

              <Select
                label="Select AI Model"
                value={model}
                onChange={handleModelChange}
              >
                <MenuItem value="">Select Model</MenuItem>
                <MenuItem value="gpt-3.5-turbo">ChatGPT</MenuItem>
                <MenuItem value="gemini-1.5-flash">Google Gemini</MenuItem>
              </Select>
            </FormControl>
          </ListItem>
          <ListItem>
            <TextField
              fullWidth
              label="Enter API Key"
              value={apiInput}
              onChange={(e) => setApiInput(e.target.value)}
            />
          </ListItem>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleApiKeyChange} variant="contained">
            Submit API Key
          </Button>
        </DialogActions>
      </Dialog>
    </Drawer>
  );
};

export default Sidebar;

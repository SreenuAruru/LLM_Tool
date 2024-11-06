import React, { useState, useEffect } from "react";
import {
  TextField,
  IconButton,
  Box,
  Typography,
  InputAdornment,
  Paper,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import axios from "axios";
import { toast } from "react-toastify";
import { FaDatabase } from "react-icons/fa";
import { MdDelete } from "react-icons/md";

const MainContent = ({ apiKey, selectedModel, storeId }) => {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [dbCredentials, setDbCredentials] = useState({
    host: "",
    user: "",
    password: "",
    database: "",
  });
  const storedCredentials = JSON.parse(localStorage.getItem("dbCredentials"));
  console.log("storedCredentials", storedCredentials);

  const handleSend = async (isGeneralQuestion = false) => {
    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("user_question", question);
      formData.append("user_api_key", apiKey);
      formData.append("model_name", selectedModel);
      if (!isGeneralQuestion) {
        formData.append("store_id", storeId); // Only send store_id if it's not a general question
      }
      console.log("user_api_key", apiKey);

      const response = await axios.post(
        "http://localhost:8000/ask-question/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const botResponse = response.data.response;
      setChatHistory([
        ...chatHistory,
        { sender: "user", text: question },
        { sender: "bot", text: botResponse },
      ]);
      setQuestion("");
    } catch (error) {
      console.error("Error asking question:", error);
      toast.error("Error asking question");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log("Selected Model:", selectedModel);
  }, [selectedModel]);

  useEffect(() => {
    const savedDbCredentials = JSON.parse(
      localStorage.getItem("dbCredentials")
    );
    if (savedDbCredentials) {
      setDbCredentials(savedDbCredentials);
    }
  }, []);

  const handleOpenPopup = () => {
    setOpen(true);
  };

  const handleClosePopup = () => {
    setOpen(false);
  };

  const handleSaveCredentials = async () => {
    if (
      !dbCredentials.host ||
      !dbCredentials.user ||
      !dbCredentials.password ||
      !dbCredentials.database
    ) {
      toast.error("Please fill all fields!");
      return;
    }
    try {
      window.location.reload();
      const response = await axios.post(
        "http://localhost:8000/set-database-credentials/",
        dbCredentials
      );
      console.log("------>db", dbCredentials);
      toast.success(response.data.message);
      localStorage.setItem("dbCredentials", JSON.stringify(dbCredentials));
    } catch (error) {
      toast.error(`Error: ${error.response?.data?.detail || error.message}`);
    }

    handleClosePopup();
  };

  const handleDeleteCredential = async () => {
    setDbCredentials({ host: "", user: "", password: "", database: "" });
    localStorage.removeItem("dbCredentials");
    // toast.success("Database connection removed!");
    await fetch("http://localhost:8000/clear-database-credentials/", {
      method: "POST",
    });

    alert("Database credentials removed.");
    window.location.reload();
  };

  return (
    <Box sx={{ height: "97vh", display: "flex", flexDirection: "column" }}>
      <Box
        sx={{
          p: 1,
          borderBottom: "1px solid #ddd",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Typography variant="h6" sx={{ ml: 1 }}>
          {selectedModel ? `Asking ${selectedModel}` : "Please select a model"}
        </Typography>
        <IconButton onClick={handleOpenPopup}>
          <FaDatabase color="#0087ff" />
        </IconButton>
      </Box>
      <Box sx={{ flex: 1, overflowY: "auto", p: 2 }}>
        {chatHistory.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              justifyContent:
                message.sender === "user" ? "flex-end" : "flex-start",
              mb: 1,
            }}
          >
            <Typography>
              {message.sender === "user" && (
                <span style={{ fontStyle: "italic", fontSize: "small" }}>
                  (Source: <strong>{message.source}</strong>)
                </span>
              )}{" "}
            </Typography>
            <Paper
              sx={{
                backgroundColor:
                  message.sender === "user" ? "#DCF8C6" : "#E5E5EA",
                color: "#000",
                borderRadius: 2,
                padding: "8px 12px",
                maxWidth: "70%",
                wordWrap: "break-word",
                alignSelf:
                  message.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              <Typography variant="body1">{message.text} </Typography>
            </Paper>
          </Box>
        ))}
      </Box>
      <Box
        sx={{
          p: 1,
          backgroundColor: "#fff",
          borderTop: "1px solid #ddd",
          display: "flex",
          alignItems: "center",
          position: "sticky",
          bottom: 0,
          zIndex: 1,
        }}
      >
        <TextField
          fullWidth
          placeholder="Ask your question here..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter" && !loading && question.trim()) {
              handleSend();
            }
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => handleSend(false)}
                  disabled={loading || !question.trim()}
                  sx={{
                    backgroundColor: loading ? "transparent" : "#1976d2",
                    "&:hover": {
                      backgroundColor: loading ? "transparent" : "#1565c0",
                    },
                  }}
                >
                  {loading ? (
                    <CircularProgress size={24} />
                  ) : (
                    <SendIcon sx={{ color: "#fff" }} />
                  )}
                </IconButton>
              </InputAdornment>
            ),
          }}
          sx={{ mr: 1, maxWidth: "calc(100% - 60px)" }}
        />
        <Button
          onClick={() => handleSend(true)} // Pass true to indicate a general question
          variant="contained"
          disabled={loading || !question.trim()}
        >
          General
        </Button>
      </Box>

      {/* Database Credentials Popup */}
      <Dialog open={open} onClose={handleClosePopup}>
        <DialogTitle>Database Credentials</DialogTitle>
        <DialogContent>
          <TextField
            label="Host"
            value={dbCredentials.host}
            onChange={(e) =>
              setDbCredentials({ ...dbCredentials, host: e.target.value })
            }
            fullWidth
            margin="normal"
          />
          <TextField
            label="User"
            value={dbCredentials.user}
            onChange={(e) =>
              setDbCredentials({ ...dbCredentials, user: e.target.value })
            }
            fullWidth
            margin="normal"
          />
          <TextField
            label="Password"
            type="password"
            value={dbCredentials.password}
            onChange={(e) =>
              setDbCredentials({ ...dbCredentials, password: e.target.value })
            }
            fullWidth
            margin="normal"
          />
          <TextField
            label="Database"
            value={dbCredentials.database}
            onChange={(e) =>
              setDbCredentials({ ...dbCredentials, database: e.target.value })
            }
            fullWidth
            margin="normal"
          />
          <List>
            {
              <ListItem>
                <ListItemText
                  primary={`${dbCredentials.user}@${dbCredentials.host}`}
                  secondary={dbCredentials.database}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    onClick={() => handleDeleteCredential()}
                  >
                    <MdDelete color="red" />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            }
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePopup} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSaveCredentials} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MainContent;

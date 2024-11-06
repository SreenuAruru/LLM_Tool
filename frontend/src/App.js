import React, { useState } from "react";
import { Container, Grid } from "@mui/material";
import Sidebar from "./components/Sidebar";
import MainContent from "./components/MainContent";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const App = () => {
  const [storeId, setStoreId] = useState(null);
  const [apiKey, setApiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  console.log("selectedModel", selectedModel);
  return (
    <Container maxWidth="xl">
      <ToastContainer />
      <Grid container spacing={2}>
        <Grid item xs={3}>
          <Sidebar
            setStoreId={setStoreId}
            setApiKey={setApiKey}
            setSelectedModel={setSelectedModel}
          />
        </Grid>
        <Grid item xs={9}>
          <MainContent
            storeId={storeId}
            apiKey={apiKey}
            selectedModel={selectedModel}
          />
        </Grid>
      </Grid>
    </Container>
  );
};

export default App;

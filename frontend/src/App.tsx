import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout.js";
import { StandardsPage } from "./pages/StandardsPage.js";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<StandardsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

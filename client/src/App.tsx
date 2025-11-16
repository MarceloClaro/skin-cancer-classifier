import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ClientOnly } from "./components/ClientOnly";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import SkinClassifier from "./pages/SkinClassifier";
import TrainingVisualization from "./pages/TrainingVisualization";
import RetrainingInterface from "./pages/RetrainingInterface";
import AdminDataset from "./pages/AdminDataset";
import Header from "./components/Header";

function Router() {
  // make sure to consider if you need authentication for certain routes
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/classificador"} component={SkinClassifier} />
      <Route path={"/treinamento"} component={TrainingVisualization} />
      <Route path={"/admin/retreinar"} component={RetrainingInterface} />
      <Route path={"/admin/dataset"} component={AdminDataset} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <ClientOnly>
            <Toaster />
          </ClientOnly>
          <Header />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;

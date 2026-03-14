import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MapView } from './components/MapView';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="w-full h-screen">
        <MapView />
      </div>
    </QueryClientProvider>
  );
}

export default App;

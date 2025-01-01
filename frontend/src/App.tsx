import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom';
import Authentication from './pages/authentication';
import Home from './pages/home';

const App = () => {
  const router = createBrowserRouter([
    {
      path: '/',
      element: <Authentication />
    },
    {
      path: '/home',
      element: <Home />
    }
  ]);

  return <RouterProvider router={router} />;
}

export default App;

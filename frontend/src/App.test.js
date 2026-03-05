import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from './App';

jest.mock('axios');

const mockTasks = [
  { id: 1, title: 'Task 1', description: 'Desc 1', is_active: true, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
  { id: 2, title: 'Task 2', description: 'Desc 2', is_active: false, created_at: '2024-01-01T00:00:00Z', updated_at: '2024-01-01T00:00:00Z' },
];

const mockStats = { total: 2, active: 1, done: 1 };

beforeEach(() => {
  jest.clearAllMocks();
  axios.get.mockImplementation((url) => {
    if (url.includes('/stats')) return Promise.resolve({ data: mockStats });
    if (url.includes('/tasks')) return Promise.resolve({ data: mockTasks });
    if (url.includes('/search')) return Promise.resolve({ data: [mockTasks[0]] });
    return Promise.resolve({ data: {} });
  });
  axios.post.mockResolvedValue({ data: mockTasks[0] });
  axios.put.mockResolvedValue({ data: { ...mockTasks[0], is_active: false } });
  axios.delete.mockResolvedValue({ data: '' });
});

test('renders the app title', async () => {
  render(<App />);
  expect(screen.getByText(/Task Manager/i)).toBeInTheDocument();
});

test('fetches and displays tasks on load', async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });
});

test('displays stats', async () => {
  render(<App />);
  await waitFor(() => {
    expect(screen.getByText(/2 total/)).toBeInTheDocument();
    expect(screen.getByText(/1 active/)).toBeInTheDocument();
    expect(screen.getByText(/1 done/)).toBeInTheDocument();
  });
});

test('filter buttons are rendered', async () => {
  render(<App />);
  expect(screen.getByText('All')).toBeInTheDocument();
  expect(screen.getByText('Active')).toBeInTheDocument();
  expect(screen.getByText('Done')).toBeInTheDocument();
  expect(screen.getByText('Today')).toBeInTheDocument();
});

test('clicking filter button triggers new fetch', async () => {
  render(<App />);
  await waitFor(() => expect(axios.get).toHaveBeenCalled());

  const initialCalls = axios.get.mock.calls.length;
  fireEvent.click(screen.getByText('Active'));

  await waitFor(() => {
    expect(axios.get.mock.calls.length).toBeGreaterThan(initialCalls);
  });
});

import { useState, useEffect, useMemo } from 'react';
import { 
  Button, 
  DataTable, 
  Dialog, 
  Field, 
  Input, 
  Flex, 
  Grid, 
  Box, 
  Title, 
  Icon, 
  useToast 
} from './weg-ui-mock'; // Using mocks for demonstration
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  priority: string;
}

const taskSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  description: z.string().optional(),
  priority: z.string().default('Baixa'),
});

type TaskFormData = z.infer<typeof taskSchema>;

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const { toast } = useToast();

  const { control, handleSubmit, reset, formState: { errors } } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: { title: '', description: '', priority: 'Baixa' }
  });

  const fetchTasks = async () => {
    setIsLoading(true);
    try {
      const res = await axios.get(`${API_URL}/tasks/`);
      setTasks(res.data);
    } catch (err) {
      toast({ status: 'error', title: 'Erro ao carregar tarefas' });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const onSubmit = async (data: TaskFormData) => {
    try {
      if (editingTask) {
        await axios.put(`${API_URL}/tasks/${editingTask.id}`, data);
        toast({ status: 'success', title: 'Tarefa atualizada' });
      } else {
        await axios.post(`${API_URL}/tasks/`, data);
        toast({ status: 'success', title: 'Tarefa criada' });
      }
      setIsDialogOpen(false);
      setEditingTask(null);
      reset({ title: '', description: '', priority: 'Baixa' });
      fetchTasks();
    } catch (err) {
      toast({ status: 'error', title: 'Erro ao salvar tarefa' });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/tasks/${id}`);
      toast({ status: 'success', title: 'Tarefa removida' });
      fetchTasks();
    } catch (err) {
      toast({ status: 'error', title: 'Erro ao remover tarefa' });
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      await axios.patch(`${API_URL}/tasks/${task.id}/complete?completed=${!task.completed}`);
      fetchTasks();
    } catch (err) {
      toast({ status: 'error', title: 'Erro ao atualizar status' });
    }
  };

  const columns = useMemo(() => [
    { field: 'id', headerName: 'ID' },
    { field: 'title', headerName: 'Título' },
    { field: 'priority', headerName: 'Prioridade' },
    { 
      field: 'completed', 
      headerName: 'Status',
      cellRenderer: (params: any) => (
        <Button 
          onClick={() => handleToggleComplete(params.data)}
          color={params.value ? 'neutral' : 'primary'}
        >
          {params.value ? 'Concluída' : 'Pendente'}
        </Button>
      )
    },
    {
      headerName: 'Ações',
      cellRenderer: (params: any) => (
        <Flex gap="small">
          <Button onClick={() => { setEditingTask(params.data); reset(params.data); setIsDialogOpen(true); }}>
            <Icon name="pencil" />
          </Button>
          <Button color="neutral" onClick={() => handleDelete(params.data.id)}>
            <Icon name="trash" />
          </Button>
        </Flex>
      )
    }
  ], []);

  return (
    <Box p="large">
      <Flex justify="space-between" align="center">
        <Title level={1}>Gerenciador de Tarefas</Title>
        <Button color="primary" onClick={() => { setEditingTask(null); reset({ title: '', description: '', priority: 'Baixa' }); setIsDialogOpen(true); }}>
          Nova Tarefa
        </Button>
      </Flex>

      <DataTable 
        rowData={tasks} 
        columnDefs={columns}
        loading={isLoading}
      />

      <Dialog open={isDialogOpen}>
        <Dialog.Content title={editingTask ? 'Editar Tarefa' : 'Nova Tarefa'}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid gap="medium">
              <Grid.Cell span={12}>
                <Controller
                  name="title"
                  control={control}
                  render={({ field }) => (
                    <Field label="Título" statusText={errors.title?.message}>
                      <Input.Text {...field} />
                    </Field>
                  )}
                />
              </Grid.Cell>
              <Grid.Cell span={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <Field label="Descrição">
                      <Input.Text {...field} />
                    </Field>
                  )}
                />
              </Grid.Cell>
              <Grid.Cell span={12}>
                <Controller
                  name="priority"
                  control={control}
                  render={({ field }) => (
                    <Field label="Prioridade">
                      <Input.Select {...field} options={[
                        { label: 'Baixa', value: 'Baixa' },
                        { label: 'Média', value: 'Média' },
                        { label: 'Alta', value: 'Alta' }
                      ]} />
                    </Field>
                  )}
                />
              </Grid.Cell>
            </Grid>
            <Flex justify="end" style={{ marginTop: '20px' }}>
              <Button type="button" onClick={() => setIsDialogOpen(false)}>Cancelar</Button>
              <Button color="primary" type="submit">Salvar</Button>
            </Flex>
          </form>
        </Dialog.Content>
      </Dialog>
    </Box>
  );
}

export default App;

import { useState, useEffect, useMemo } from 'react';
import type { ChangeEvent } from 'react';
import './App.css';
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

type AppView = 'tasks' | 'room-booking';

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
  priority: z.string().min(1),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface RoomReservation {
  id: number;
  roomId: string;
  bookingDate: string;
  startTime: string;
  endTime: string;
}

interface RoomBookingFormData {
  roomId: string;
  bookingDate: string;
  startTime: string;
  endTime: string;
}

interface RoomBookingResult {
  canReserve: boolean;
  message: string;
  conflictingReservations: RoomReservation[];
}

const existingRoomReservations: RoomReservation[] = [
  {
    id: 1,
    roomId: 'SALA-01',
    bookingDate: '2026-09-26',
    startTime: '10:00',
    endTime: '11:00',
  },
  {
    id: 2,
    roomId: 'SALA-02',
    bookingDate: '2026-09-26',
    startTime: '14:00',
    endTime: '15:00',
  },
];

const initialRoomBookingForm: RoomBookingFormData = {
  roomId: 'SALA-01',
  bookingDate: '2026-09-26',
  startTime: '10:30',
  endTime: '11:30',
};

function reservationOverlaps(
  requestedReservation: RoomBookingFormData,
  existingReservation: RoomReservation,
) {
  const isSameRoom = requestedReservation.roomId === existingReservation.roomId;
  const isSameDate =
    requestedReservation.bookingDate === existingReservation.bookingDate;

  return (
    isSameRoom &&
    isSameDate &&
    requestedReservation.startTime < existingReservation.endTime &&
    requestedReservation.endTime > existingReservation.startTime
  );
}

function checkRoomBookingConflicts(
  requestedReservation: RoomBookingFormData,
): RoomBookingResult {
  if (!requestedReservation.roomId.trim()) {
    return {
      canReserve: false,
      message: 'Informe a sala antes de validar.',
      conflictingReservations: [],
    };
  }

  if (requestedReservation.endTime <= requestedReservation.startTime) {
    return {
      canReserve: false,
      message: 'O horario final deve ser posterior ao horario inicial.',
      conflictingReservations: [],
    };
  }

  const conflictingReservations = existingRoomReservations.filter(
    (existingReservation) =>
      reservationOverlaps(requestedReservation, existingReservation),
  );

  if (conflictingReservations.length > 0) {
    return {
      canReserve: false,
      message: 'Reserva indisponivel: existe conflito para a mesma sala e dia.',
      conflictingReservations,
    };
  }

  return {
    canReserve: true,
    message: 'Reserva disponivel para o horario solicitado.',
    conflictingReservations: [],
  };
}

function App() {
  const [currentView, setCurrentView] = useState<AppView>('tasks');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [roomBookingForm, setRoomBookingForm] = useState<RoomBookingFormData>(
    initialRoomBookingForm,
  );
  const [roomBookingResult, setRoomBookingResult] =
    useState<RoomBookingResult | null>(null);
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

  const updateRoomBookingField = (
    field: keyof RoomBookingFormData,
    value: string,
  ) => {
    setRoomBookingForm((currentForm) => ({
      ...currentForm,
      [field]: value,
    }));
    setRoomBookingResult(null);
  };

  const validateRoomBooking = () => {
    setRoomBookingResult(checkRoomBookingConflicts(roomBookingForm));
  };

  return (
    <Box p="large" className="app-shell">
      <Flex justify="space-between" align="center" style={{ flexWrap: 'wrap' }}>
        <Title level={1}>MVP Pos UFG</Title>
        <nav className="view-tabs" aria-label="Areas da aplicacao">
          <button
            className={currentView === 'tasks' ? 'active' : ''}
            onClick={() => setCurrentView('tasks')}
            type="button"
          >
            Tarefas
          </button>
          <button
            className={currentView === 'room-booking' ? 'active' : ''}
            onClick={() => setCurrentView('room-booking')}
            type="button"
          >
            Reserva de Sala
          </button>
        </nav>
      </Flex>

      {currentView === 'tasks' && (
        <section className="content-section">
          <Flex justify="space-between" align="center">
            <Title level={2}>Gerenciador de Tarefas</Title>
            <Button color="primary" onClick={() => { setEditingTask(null); reset({ title: '', description: '', priority: 'Baixa' }); setIsDialogOpen(true); }}>
              Nova Tarefa
            </Button>
          </Flex>

          <DataTable 
            rowData={tasks} 
            columnDefs={columns}
            loading={isLoading}
          />
        </section>
      )}

      {currentView === 'room-booking' && (
        <section className="content-section room-booking">
          <div>
            <Title level={2}>Validador de Reserva de Sala</Title>
            <p className="section-copy">
              Teste a regra de conflito com dados ficticios: SALA-01 ja esta
              reservada em 26/09/2026 das 10:00 as 11:00.
            </p>
          </div>

          <div className="booking-layout">
            <form
              className="booking-form"
              onSubmit={(event) => {
                event.preventDefault();
                validateRoomBooking();
              }}
            >
              <Field label="Sala">
                <Input.Select
                  value={roomBookingForm.roomId}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) =>
                    updateRoomBookingField('roomId', event.target.value)
                  }
                  options={[
                    { label: 'SALA-01', value: 'SALA-01' },
                    { label: 'SALA-02', value: 'SALA-02' },
                    { label: 'Sala vazia (erro)', value: ' ' },
                  ]}
                />
              </Field>
              <Field label="Data">
                <Input.Text
                  type="date"
                  value={roomBookingForm.bookingDate}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateRoomBookingField('bookingDate', event.target.value)
                  }
                />
              </Field>
              <Field label="Inicio">
                <Input.Text
                  type="time"
                  value={roomBookingForm.startTime}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateRoomBookingField('startTime', event.target.value)
                  }
                />
              </Field>
              <Field label="Fim">
                <Input.Text
                  type="time"
                  value={roomBookingForm.endTime}
                  onChange={(event: ChangeEvent<HTMLInputElement>) =>
                    updateRoomBookingField('endTime', event.target.value)
                  }
                />
              </Field>
              <Button color="primary" type="submit">
                Validar reserva
              </Button>
            </form>

            <div className="booking-panel">
              <h3>Reservas existentes</h3>
              <ul className="reservation-list">
                {existingRoomReservations.map((reservation) => (
                  <li key={reservation.id}>
                    <strong>{reservation.roomId}</strong>
                    <span>{reservation.bookingDate}</span>
                    <span>
                      {reservation.startTime} - {reservation.endTime}
                    </span>
                  </li>
                ))}
              </ul>

              {roomBookingResult && (
                <div
                  className={
                    roomBookingResult.canReserve
                      ? 'booking-result success'
                      : 'booking-result error'
                  }
                >
                  <strong>
                    {roomBookingResult.canReserve
                      ? 'Pode reservar'
                      : 'Nao pode reservar'}
                  </strong>
                  <p>{roomBookingResult.message}</p>
                  {roomBookingResult.conflictingReservations.length > 0 && (
                    <ul>
                      {roomBookingResult.conflictingReservations.map(
                        (reservation) => (
                          <li key={reservation.id}>
                            Conflito com {reservation.roomId},{' '}
                            {reservation.startTime} - {reservation.endTime}
                          </li>
                        ),
                      )}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      )}

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

import React from 'react';

// Simplified Mocks for @weg-react-ui to allow local running without the private registry
export const Button = ({ children, color, onClick, ...props }: any) => (
  <button 
    onClick={onClick}
    style={{ 
      padding: '8px 16px', 
      backgroundColor: color === 'primary' ? '#00579d' : '#f0f0f0',
      color: color === 'primary' ? 'white' : 'black',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer'
    }}
    {...props}
  >
    {children}
  </button>
);

export const DataTable = ({ rowData, columnDefs, loading }: any) => (
  <div style={{ width: '100%', overflowX: 'auto', marginTop: '20px' }}>
    {loading ? <p>Carregando...</p> : (
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ddd' }}>
            {columnDefs.map((col: any) => <th key={col.headerName} style={{ textAlign: 'left', padding: '12px' }}>{col.headerName}</th>)}
          </tr>
        </thead>
        <tbody>
          {rowData.map((row: any) => (
            <tr key={row.id} style={{ borderBottom: '1px solid #eee' }}>
              {columnDefs.map((col: any) => (
                <td key={col.headerName} style={{ padding: '12px' }}>
                  {col.cellRenderer ? col.cellRenderer({ data: row, value: row[col.field] }) : row[col.field]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    )}
  </div>
);

export const Dialog = ({ open, children }: any) => open ? (
  <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyCenter: 'center', zIndex: 1000 }}>
    <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', maxWidth: '500px', width: '100%' }}>
      {children}
    </div>
  </div>
) : null;

Dialog.Content = ({ title, children }: any) => (
  <div>
    <h2>{title}</h2>
    {children}
  </div>
);

export const Field = ({ label, children, statusText }: any) => (
  <div style={{ marginBottom: '16px' }}>
    <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>{label}</label>
    {children}
    {statusText && <span style={{ color: 'red', fontSize: '12px' }}>{statusText}</span>}
  </div>
);

export const Input = {
  Text: (props: any) => <input type="text" style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }} {...props} />,
  Select: ({ options, ...props }: any) => (
    <select style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }} {...props}>
      {options.map((opt: any) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
    </select>
  )
};

export const Flex = ({ children, gap, justify, align, direction, style, ...props }: any) => (
  <div style={{ display: 'flex', gap: gap === 'small' ? '8px' : '16px', justifyContent: justify, alignItems: align, flexDirection: direction, ...style }} {...props}>
    {children}
  </div>
);

export const Grid = ({ children, gap }: any) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '16px' }}>
    {children}
  </div>
);

Grid.Cell = ({ children, span }: any) => (
  <div style={{ gridColumn: `span ${typeof span === 'number' ? span : 12}` }}>
    {children}
  </div>
);

export const Box = ({ children, p, ...props }: any) => <div style={{ padding: p === 'large' ? '24px' : '12px' }} {...props}>{children}</div>;
export const Title = ({ children, level }: any) => React.createElement(`h${level || 1}`, {}, children);
export const Text = ({ children }: any) => <p>{children}</p>;
export const Icon = ({ name }: any) => <span>[{name}]</span>;
export const useToast = () => ({ toast: (params: any) => console.log('Toast:', params.title) });

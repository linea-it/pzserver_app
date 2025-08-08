import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Tab,
  Tabs
} from '@mui/material';
import DialogActions from '@mui/material/DialogActions';
import PropTypes from 'prop-types';
import * as React from 'react';

function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

export default function ProcessLogs({
  isOpen,
  handleProcessLogsDialogOpen,
  productName,
  pipelineOut = '',
  schedulerOut = ''
}) {

  const [value, setValue] = React.useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Dialog
      open={isOpen}
      onClose={handleProcessLogsDialogOpen}
      PaperProps={{
        style: { height: '80vh' }
      }}
      fullWidth={true}
      maxWidth="md"
    >
      <DialogTitle>
        Process log - {productName}
      </DialogTitle>
        <Tabs value={value} onChange={handleChange}>
          <Tab label="Pipeline" {...a11yProps(0)} />
          <Tab label="Scheduler" {...a11yProps(1)} />
        </Tabs>
        <DialogContent dividers style={{ padding: '0px' }}>
          <CustomTabPanel value={value} index={0}>
            <DialogContentText
              id="scroll-dialog-description"
              tabIndex={-1}
              style={{ fontSize: '0.9rem' }}
            >
              {pipelineOut ? (
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: '0px' }}>
                  {pipelineOut}
                </pre>
                ) : (
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: '0px' }}>
                    <span>No logs available for this process.</span>
                  </pre>
                )}
            </DialogContentText>
        </CustomTabPanel>
        <CustomTabPanel value={value} index={1}>
            <DialogContentText
              id="scroll-dialog-description"
              tabIndex={-1}
              style={{ fontSize: '0.9rem' }}
            >
              {schedulerOut ? (
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: '0px' }}>
                  {schedulerOut}
                </pre>
                ) : (
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: '0px' }}>
                    <span>No logs available for this process.</span>
                  </pre>
                )}
            </DialogContentText>
          </CustomTabPanel>
        </DialogContent>
      <DialogActions>
        <Button onClick={handleProcessLogsDialogOpen}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}

ProcessLogs.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  handleProcessLogsDialogOpen: PropTypes.func.isRequired,
  productName: PropTypes.string.isRequired,
  pipelineOut: PropTypes.string,
  schedulerOut: PropTypes.string,
}

/**
 * Settings page (Clay), shown inside the Pebble app on the phone.
 * Camera credentials stay on the phone; only the operating values are
 * forwarded to the watch.
 */

var CAMERA_SLOTS = 8;

var config = [
  { type: 'heading', defaultValue: 'PTZ Remote' },
  {
    type: 'text',
    defaultValue: 'Remote control for Panasonic PTZ cameras (AW series). ' +
      'The camera has to be reachable from the phone, on the same network.'
  },

  {
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'Operation' },
      {
        type: 'slider',
        messageKey: 'cfgSpeed',
        label: 'Speed level',
        description: 'How much of the camera’s maximum speed the watch uses. ' +
          'For moves during a running show, 1 or 2 is usually plenty.',
        defaultValue: 3, min: 1, max: 5, step: 1
      },
      {
        type: 'slider',
        messageKey: 'cfgPresetCount',
        label: 'Presets in the menu',
        defaultValue: 8, min: 1, max: 24, step: 1
      },
      {
        type: 'select',
        messageKey: 'presetOffset',
        label: 'Preset numbering',
        description: 'Panasonic counts from zero internally. If preset 1 on the watch ' +
          'recalls the wrong position, switch this.',
        defaultValue: '0',
        options: [
          { label: 'Preset 1 = camera memory 0 (default)', value: '0' },
          { label: 'Preset 1 = camera memory 1', value: '1' }
        ]
      },
      {
        type: 'toggle',
        messageKey: 'cfgVibrate',
        label: 'Vibrate on error',
        defaultValue: true
      }
    ]
  },

  {
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'Motion control' },
      {
        type: 'text',
        defaultValue: 'The watch measures tilt against gravity. Zero is always the ' +
          'posture your wrist is in the moment you press the dead-man button, ' +
          'so you can drive the camera from any comfortable arm position.'
      },
      {
        type: 'slider',
        messageKey: 'cfgGyroSens',
        label: 'Sensitivity',
        description: '1 asks for a clear movement (about 40 degrees for full speed), ' +
          '10 reacts to a short flick of the wrist (about 12 degrees).',
        defaultValue: 5, min: 1, max: 10, step: 1
      },
      {
        type: 'slider',
        messageKey: 'cfgGyroDead',
        label: 'Dead zone',
        description: 'How still your hand has to be before the camera starts moving. ' +
          'Larger means more forgiving.',
        defaultValue: 60, min: 20, max: 200, step: 10
      },
      {
        type: 'select',
        messageKey: 'cfgGyroLock',
        label: 'Axes at start',
        defaultValue: '0',
        options: [
          { label: 'Pan + tilt', value: '0' },
          { label: 'Pan + zoom', value: '1' },
          { label: 'Tilt only', value: '2' }
        ]
      },
      { type: 'toggle', messageKey: 'cfgInvertPan',  label: 'Invert pan',  defaultValue: false },
      { type: 'toggle', messageKey: 'cfgInvertTilt', label: 'Invert tilt', defaultValue: false }
    ]
  },

  {
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'Preview image' },
      {
        type: 'text',
        defaultValue: 'The watch can fetch a still frame after each move and each preset. ' +
          'Not a live feed: the Bluetooth link to the watch carries about 1.6 KB per ' +
          'second, so one image takes one to three seconds. Nothing is transferred ' +
          'while the camera is moving, so control commands keep priority. Can also be ' +
          'switched on and off in the menu on the watch. Beta — not yet verified ' +
          'against real camera hardware.'
      },
      {
        type: 'toggle',
        messageKey: 'cfgPreview',
        label: 'Enable preview',
        defaultValue: false
      },
      {
        type: 'select',
        messageKey: 'cfgPreviewSize',
        label: 'Image size',
        defaultValue: '1',
        options: [
          { label: 'Small — 64 px wide, about 1 s', value: '0' },
          { label: 'Medium — 96 px wide, about 2 s', value: '1' },
          { label: 'Large — 128 px wide, about 3 s', value: '2' }
        ]
      }
    ]
  }
];

// One block per camera. Blocks left empty do not show up on the watch.
for (var i = 1; i <= CAMERA_SLOTS; i++) {
  config.push({
    type: 'section',
    items: [
      { type: 'heading', defaultValue: 'Camera ' + i },
      {
        type: 'input',
        messageKey: 'cam' + i + 'Name',
        label: 'Name',
        defaultValue: i === 1 ? 'Camera 1' : '',
        attributes: { placeholder: 'e.g. Stage left', maxlength: 24 }
      },
      {
        type: 'input',
        messageKey: 'cam' + i + 'Host',
        label: 'IP address',
        defaultValue: '',
        attributes: { placeholder: '192.168.0.10' }
      },
      {
        type: 'input',
        messageKey: 'cam' + i + 'Port',
        label: 'Port',
        defaultValue: '80',
        attributes: { placeholder: '80', type: 'number' }
      },
      {
        type: 'input',
        messageKey: 'cam' + i + 'User',
        label: 'User (optional)',
        defaultValue: '',
        attributes: { placeholder: 'admin' }
      },
      {
        type: 'input',
        messageKey: 'cam' + i + 'Pass',
        label: 'Password (optional)',
        defaultValue: '',
        attributes: { type: 'password' }
      }
    ]
  });
}

config.push({ type: 'submit', defaultValue: 'Save' });

// Below the save button, so the thank-you does not interrupt the form.
config.push({
  type: 'section',
  items: [
    { type: 'heading', defaultValue: 'Support' },
    {
      type: 'text',
      defaultValue: 'The app is free and has no ads. If you enjoy it, a coffee is much ' +
        'appreciated: <a href="https://buymeacoffee.com/SIDEffects" target="_blank">' +
        'buymeacoffee.com/SIDEffects</a>'
    },
    { type: 'button', id: 'donate', primary: true, defaultValue: '☕ Buy me a coffee' }
  ]
});

module.exports = config;

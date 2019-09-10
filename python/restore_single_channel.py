channel = 4



with open('/u/bviola/work/saved/den_chan'+str(channel)+'.pkl',
                  'rb') as f:  # Python 3: open(..., 'rb')
            [self.data.KG1_data.density[channel]] = pickle.load(f)
f.close()
if channel >4:
    with open('/u/bviola/work/saved/vib_chan'+str(channel)+'.pkl',
              'rb') as f:  # Python 3: open(..., 'rb')
        [self.data.KG1_data.vibration[channel]] = pickle.load(f)
    f.close()
# with open('/u/bviola/work/saved/fj_dcn_chan'+str(channel)+'.pkl',
#           'rb') as f:  # Python 3: open(..., 'rb')
#     [self.data.KG1_data.fj_dcn[channel]] = pickle.load(f)
# f.close()

with open('/u/bviola/work/saved/fj_met_chan'+str(channel)+'.pkl',
          'rb') as f:  # Python 3: open(..., 'rb')
    [self.data.KG1_data.fj_met[channel]] = pickle.load(f)
f.close()
self.data.SF_ch4 = 0
self.data.data_changed[channel - 1] = True
self.data.statusflag_changed[channel-1] = True
self.update_channel(channel)
self.save_kg1('scratch')


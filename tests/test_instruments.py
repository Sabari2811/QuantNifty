from engine.instrument_manager import InstrumentManager

manager = InstrumentManager()

manager.download_instruments("index")
manager.download_instruments("equity")
manager.download_instruments("fno")
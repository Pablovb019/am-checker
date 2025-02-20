import logging
import coloredlogs

SUCCESS = 25
logging.addLevelName(SUCCESS, 'SUCCESS')

class CustomLogger(logging.Logger):
    def defineLogger(self):
        coloredlogs.install(
            logger=self,
            level='DEBUG',
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            level_styles={
                'info': {'color': 'blue'},
                'error': {'color': 'red'},
                'warning': {'color': 'yellow'},
                'success': {'color': 'green'},
                'debug': {'color': 'magenta'}
            },
            field_styles={
                'levelname': {'bold': True, 'color': 'cyan'},
                'asctime': {'color': 'white'}
            }
        )

    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, message, args, **kwargs)



Logger = CustomLogger('TFG')
Logger.setLevel(logging.DEBUG)
Logger.defineLogger()
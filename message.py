import re


# message
class Message:
    @staticmethod
    def format(message, *args):

        if message:
            splits = re.split("(\{\})", message)
            index = 0
            for (i, split) in enumerate(splits):
                if "{}" == split:
                    splits[i] = "{" + str(index) + "}"
                    index += 1
            message = "".join(splits)

            try:
                message = message.format(*args)
            finally:
                pass
        return message



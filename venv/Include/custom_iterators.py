class CustomIterator:

    def __init__(self,token_list):
        self.token_list = token_list
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter>len(self.token_list):
            raise StopIteration
        else:
            self.counter+=1
            return self.token_list[self.counter]

    def back(self):
        self.counter-=1

    def if_in(self,token_type):
        for i in range(self.counter,len(self.token_list)):
            if (self.token_list[i]).type == token_type:
                return True
        return False

    def get_list(self):
        return self.token_list


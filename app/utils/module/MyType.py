class LinkedList(list):

    def next(self, index_val):
        index = self.index(index_val)
        if index == self.__len__() - 1:
            return None

        return self[index + 1]

    def prev(self, index_val):
        index = self.index(index_val)
        if index == 0:
            return None

        return self[index - 1]

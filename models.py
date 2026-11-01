from abc import ABC, abstractmethod

class LibraryItem(ABC):
    
    def __init__(self,item_id,title,available=True):
        self.item_id = item_id
        self.title = title
        self._available = bool(available)
     
    @property   
    def available(self):
        return self._available
    
    def checkout(self):
        
        if not self.__annotations__available:
            raise ValueError("Item is already checked out.")
        self._available = False
        
    def checkin(self):
        self._available = True
        
    @abstractmethod
    def loan_period_days(self):
        pass
    
    @property
    def is_lendable(self):
        return self.loan_period_days() > 0

    
    def __str__(self):
        status = "Available" if self.available else "Borrowed"
        return f"{self.item_id} | {self.title} | {type(self).__name__} | {status}"
    

#BOOK Inherit LibraryItem
class Book(LibraryItem):
    
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)
        
    def loan_period_days(self):
        return 14
    

#MAGZINE Inherits LibraryItem
class Magazine(LibraryItem):
    
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)
        
    def loan_period_days(self):
        return 7
    
#Reference book also inherits libarayitems
class ReferenceBook(LibraryItem):
    
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)
        
    def loan_period_days(self):
        return 0
    

class Member:
    
    def __init__(self, member_id,name,borrowing_limit):
        
        self.member_id = member_id
        self.name = name
        self.borrowing_limit = int(borrowing_limit)
        self.active_loans = set()
        
    @property
    def borrowed_count(self):
        return len(self.active_loans)
        
    @property
    def borrowed_item_ids(self):
        return tuple(self.active_loans)
    
    def add_loan(self,item_id):
        if not self.can_borrow():
            raise ValueError("Borrowing limit reached.")
        self._active_loans.add(item_id)
        
    def remove_loan(self, item_id):
        self._active_loans.discard(item_id)

    def clear_loans(self):
        self._active_loans.clear()
        
    def __str__(self):
        return (
            f"{self.member_id} | {self.name} | "
            f"{type(self).__name__} | "
            f"{self.borrowed_count}/{self.borrowing_limit} borrowed")


#StudentMember iherits member class
class StudentMember(Member):
    
    def __init__(self,member_id,name,borrowing_limit=3):
        super().__init__(member_id, name, borrowing_limit)



class FacultyMember(Member):

    def __init__(self, member_id, name, borrowing_limit=5):
        super().__init__(member_id, name, borrowing_limit)
        

#ResearchStudent inherits StudentMember
class ResearchStudent(StudentMember):

    def __init__(self, member_id, name, borrowing_limit=5):
        super().__init__(member_id, name, borrowing_limit)


class NotificationMixin:

    def send_notice(self, message):
        print(
            f"[NOTICE to {self.name} ({self.member_id})] {message}"
        )


#NotifiedMember inherits Member and NotificationMixin
class NotifiedMember(Member, NotificationMixin):

    def __init__(self, member_id, name, borrowing_limit=3):
        super().__init__(member_id, name, borrowing_limit)
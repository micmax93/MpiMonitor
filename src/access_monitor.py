class Monitor:  # Interfejs ogólnego monitora zasobów.

    def get_in(self, id, type):
        # Uzyskanie zasobu o numerze "id" przez proces typu "type".
        pass

    def get_out(self, id):
        # Zwolnienie jednostki zasobu o numerze "id"
        pass

    def get_access(self, type):
        # Sprawdzenie czy dla danego typu znajduje się dostępny zasób.
        pass
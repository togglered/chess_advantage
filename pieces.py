import chess

PIECES = {
    'wq': chess.Piece(chess.QUEEN, chess.WHITE),
    'bq': chess.Piece(chess.QUEEN, chess.BLACK),

    'wk': chess.Piece(chess.KING, chess.WHITE),
    'bk': chess.Piece(chess.KING, chess.BLACK),

    'wr': chess.Piece(chess.ROOK, chess.WHITE),
    'br': chess.Piece(chess.ROOK, chess.BLACK),

    'wp': chess.Piece(chess.PAWN, chess.WHITE),
    'bp': chess.Piece(chess.PAWN, chess.BLACK),

    'wn': chess.Piece(chess.KNIGHT, chess.WHITE),
    'bn': chess.Piece(chess.KNIGHT, chess.BLACK),

    'wb': chess.Piece(chess.BISHOP, chess.WHITE),
    'bb': chess.Piece(chess.BISHOP, chess.BLACK),
}